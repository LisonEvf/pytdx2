from datetime import date
import math
import threading
from time import time
from typing import override
from client.baseStockClient import BaseStockClient, update_last_ack_time
from parser.market import market
from utils.block_reader import BlockReader, BlockReader_TYPE_FLAT
from const import BLOCK_FILE_TYPE, CATEGORY, KLINE_TYPE, MARKET, market_hosts
from parser.baseparser import BaseParser
from utils.log import log

class MarketClient(BaseStockClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hosts = market_hosts

    def login(self, show_info=False):
        try:
            info = self.call(market.Login())
            if show_info:
                print(info)
            return True
        except Exception as e:
            log.error("login failed: %s", e)
            return False
