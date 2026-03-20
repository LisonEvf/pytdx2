# coding=utf-8

from threading import Thread
from utils.log import log
import time

# 参考 :https://stackoverflow.com/questions/6524459/stopping-a-thread-after-a-certain-amount-of-time


DEFAULT_HEARTBEAT_INTERVAL = 15.0 # 15秒一个heartbeat

class HeartBeatThread(Thread):

    def __init__(self, client, stop_event, heartbeat, heartbeat_interval=DEFAULT_HEARTBEAT_INTERVAL):
        self.client = client
        self.stop_event = stop_event
        self.heartbeat = heartbeat
        self.heartbeat_interval = heartbeat_interval
        super(HeartBeatThread, self).__init__()
        self.last_ack_time = time.time()
    
    def update_last_ack_time(self):
        self.last_ack_time = time.time()

    def run(self):
        while not self.stop_event.is_set():
            self.stop_event.wait(self.heartbeat_interval)
            if self.client:
                # 只有在超过15秒没有新请求时才发送心跳
                # 最近一次请求是在15秒前或更早
                if time.time() - self.last_ack_time > self.heartbeat_interval:
                    try:
                        self.heartbeat()
                    except Exception as e:
                        log.debug(str(e))
                else:
                    # 15秒内有新请求，不发送心跳，等待下一次
                    continue


