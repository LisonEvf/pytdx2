from client.baseStockClient import BaseStockClient, update_last_ack_time
from parser.ex_quotation import server
from const import ex_hosts
from utils.log import log

class MarketClient(BaseStockClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hosts = ex_hosts

    def login(self, show_info=False):
        try:
            info = self.call(server.Login())
            if show_info:
                print(info)
            return True
        except Exception as e:
            log.error("login failed: %s", e)
            return False
