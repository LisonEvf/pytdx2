
import socket
import threading
import time
from parser.baseparser import BaseParser
from utils.log import log
from utils.heartbeat import HeartBeatThread

import zlib
import struct
import functools

CONNECT_TIMEOUT = 5.000
RECV_HEADER_LEN = 0x10
RSP_HEADER_LEN = 0x10

def update_last_ack_time(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        if self.heartbeat:
            self.heartbeat_thread.update_last_ack_time()
            
        current_exception = None
        try:
            ret = func(self, *args, **kw)
        except Exception as e:
            current_exception = e
            log.debug("hit exception on req exception is " + str(e))
            if self.auto_retry:
                for time_interval in self.retry_strategy.gen():
                    try:
                        time.sleep(time_interval)
                        self.disconnect()
                        self.connect(self.ip, self.port)
                        ret = func(self, *args, **kw)
                        if ret:
                            return ret
                    except Exception as retry_e:
                        current_exception = retry_e
                        log.debug(
                            "hit exception on *retry* req exception is " + str(retry_e))

                log.debug("perform auto retry on req ")

            self.last_transaction_failed = True
            ret = None
            if self.raise_exception:
                to_raise = Exception("calling function error")
                to_raise.original_exception = current_exception if current_exception else None
                raise to_raise
        """
        如果raise_exception=True 抛出异常
        如果raise_exception=False 返回None
        """
        return ret
    return wrapper

class DefaultRetryStrategy():
    """
    默认的重试策略，您可以通过写自己的重试策略替代本策略, 改策略主要实现gen方法，该方法是一个生成器，
    返回下次重试的间隔时间, 单位为秒，我们会使用 time.sleep在这里同步等待之后进行重新connect,然后再重新发起
    源请求，直到gen结束。
    """
    @classmethod
    def gen(cls):
        # 默认重试4次 ... 时间间隔如下
        for time_interval in [0.1, 0.5, 1, 2]:
            yield time_interval


class BaseStockClient():
    hosts = []
    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False): 

        self.client = None
        self.ip = None
        self.port = None

        if multithread or heartbeat:
            self.lock = threading.Lock()
        else:
            self.lock = None
        self.heartbeat = heartbeat
        self.heartbeat_thread = None
        self.stop_event = None
        self.last_transaction_failed = False

        # 是否重试
        self.auto_retry = auto_retry
        # 可以覆盖这个属性，使用新的重试策略
        self.retry_strategy = DefaultRetryStrategy()
        # 是否在函数调用出错的时候抛出异常
        self.raise_exception = raise_exception

    def call(self, parser: BaseParser):
        resp = self.send(parser.serialize())
        if resp is None:
            return None
        else:
            return parser.deserialize(resp)

    def connect(self, ip=None, port=7709, time_out=5, bind_port=None, bind_ip='0.0.0.0'):
        if ip is None:
            # 选择延迟最低的服务器连接
            infos = []
            def get_latency(ip, port, timeout):
                try:
                    start_time = time.time()
                    c = self._connect(ip, port, timeout)
                    # info = c.call(server.Info())
                    infos.append({
                        'ip': ip,
                        'port': port,
                        # 'delay': info['delay'],
                        'time': time.time() - start_time,
                    })
                except Exception as e:
                    pass
            # 多线程赛跑
            threads = []
            for host in self.hosts:
                t = threading.Thread(target=get_latency, args=(host[1], host[2], 1))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
            
            infos.sort(key=lambda x: x['time'])
            if len(infos) == 0:
                raise Exception("no available server")

            return self._connect(infos[0]['ip'], infos[0]['port'], time_out, bind_port, bind_ip)
        else:
            return self._connect(ip, port, time_out, bind_port, bind_ip)
        
    def _connect(self, ip='202.100.166.21', port=7709, time_out=CONNECT_TIMEOUT, bind_port=None, bind_ip='0.0.0.0'):
        """

        :param ip:  服务器ip 地址
        :param port:  服务器端口
        :param time_out: 连接超时时间
        :param bind_port: 绑定的本地端口
        :param bind_ip: 绑定的本地ip
        :return: 是否连接成功 True/False
        """

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.client.settimeout(time_out)
        log.debug("connecting to server : %s on port :%d" % (ip, port))

        try:
            if bind_port is not None:
                self.client.bind((bind_ip, bind_port))
            self.client.connect((ip, port))
        except socket.timeout as e:
            # print(str(e))
            log.debug("connection expired")
            if self.raise_exception:
                raise Exception("connection timeout error", e)
        except Exception as e:
            if self.raise_exception:
                raise Exception("other errors", e)

        log.debug("connected!")

        if self.heartbeat:
            self.stop_event = threading.Event()
            self.heartbeat_thread = HeartBeatThread(self.client, self.stop_event, self.doHeartBeat)
            self.heartbeat_thread.start()
        return self

    def doHeartBeat(self):
        """
        子类可以覆盖这个方法，实现自己的心跳包
        :return:
        """
        pass

    def disconnect(self):

        if self.heartbeat_thread and \
                self.heartbeat_thread.is_alive():
            self.stop_event.set()

        if self.client:
            log.debug("disconnecting")
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
            except Exception as e:
                log.debug(str(e))
                if self.raise_exception:
                    raise Exception("disconnect err")
            log.debug("disconnected")

    def send(self, data):
        """
        发送数据
        :param data:  要发送的数据
        :return:  发送成功返回True，否则返回False
        """
        if self.lock:
            with self.lock:
                return self._send(data)
        else:
            return self._send(data)

    def _send(self, data):
        """
        发送数据
        :param data:  要发送的数据
        :return:  发送成功返回True，否则返回False
        """
        if not self.client:
            log.debug("not connected")
            if self.raise_exception:
                raise Exception("not connected")

        # cunstomize: 自定义协议号
        # zipped: 0x1c 表示压缩，0xc 表示不压缩
        try:
            zipped, customize, control, zipsize, unzip_size, msg_id = struct.unpack('<BIBHHH', data[:12])
            # log.debug("sending data: zipped: %s, customize: %s, control: %s, zipsize: %d, unzip_size: %d, msg_id: %s" % (hex(zipped), hex(customize), hex(control), zipsize, unzip_size, hex(msg_id)))
            send_data = self.client.send(data)
            if send_data != len(data):
                log.debug("send data error")
                if self.raise_exception:
                    raise Exception("send data error")
            else:
                head_buf = self.client.recv(RSP_HEADER_LEN)
                
                # prefix: b1 cb 74 00 固定响应头
                prefix, zipped, customize, unknown, msg_id, zipsize, unzip_size = struct.unpack('<IBIBHHH', head_buf)
                # log.debug("recv Header: zipped: %s, customize: %s, control: %s, msg_id: %s, zipsize: %d, unzip_size: %d" % (hex(zipped), hex(customize), hex(unknown), hex(msg_id), zipsize, unzip_size))

                need_unzip_size = zipsize != unzip_size
                body_buf = bytearray()
                while zipsize > 0:
                    data_buf = self.client.recv(zipsize)
                    body_buf.extend(data_buf)
                    zipsize -= len(data_buf)
                if need_unzip_size:
                    body_buf = zlib.decompress(body_buf)

                return body_buf
        except Exception as e:
            log.debug(str(e))
            if self.raise_exception:
                raise Exception("send error")