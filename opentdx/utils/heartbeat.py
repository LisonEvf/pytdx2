# coding=utf-8

from threading import Thread
from opentdx.utils.log import log
import time

# 参考 :https://stackoverflow.com/questions/6524459/stopping-a-thread-after-a-certain-amount-of-time


DEFAULT_HEARTBEAT_INTERVAL = 15.0 # 15秒一个heartbeat
MAX_CONSECUTIVE_HEARTBEAT = 20  # 连续心跳最大次数

class HeartBeatThread(Thread):

    def __init__(self, client, stop_event, heartbeat, heartbeat_interval=DEFAULT_HEARTBEAT_INTERVAL):
        self.client = client
        self.stop_event = stop_event
        self.heartbeat = heartbeat
        self.heartbeat_interval = heartbeat_interval
        super(HeartBeatThread, self).__init__()
        self.last_ack_time = time.time()
        self._consecutive_heartbeat_count = 0  # 连续心跳计数

    def update_last_ack_time(self):
        self.last_ack_time = time.time()
        self._consecutive_heartbeat_count = 0  # 有其他通讯，重置计数器

    def run(self):
        while not self.stop_event.is_set():
            self.stop_event.wait(self.heartbeat_interval)
            if self.client:
                # 只有在超过15秒没有新请求时才发送心跳
                # 最近一次请求是在15秒前或更早
                if time.time() - self.last_ack_time > self.heartbeat_interval:
                    self._consecutive_heartbeat_count += 1
                    if self._consecutive_heartbeat_count >= MAX_CONSECUTIVE_HEARTBEAT:
                        log.debug("连续心跳达到 %d 次，断开连接", MAX_CONSECUTIVE_HEARTBEAT)
                        self.stop_event.set()
                        continue
                    try:
                        self.heartbeat()
                    except Exception as e:
                        log.debug(str(e))
                else:
                    # 15秒内有新请求，不发送心跳，等待下一次
                    continue


