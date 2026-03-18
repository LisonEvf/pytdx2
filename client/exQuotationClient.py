from datetime import date

from client.baseStockClient import BaseStockClient, update_last_ack_time
from parser.ex_quotation import ex_server, goods
from const import EX_CATEGORY, PERIOD, ex_hosts
from utils.log import log

class exQuotationClient(BaseStockClient):
    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = ex_hosts

    def login(self, show_info=False):
        try:
            info = self.call(ex_server.Login())
            if show_info:
                print(info)
            return True
        except Exception as e:
            log.error("login failed: %s", e)
            return False
    
    def server_info(self):
        try:
            info = self.call(ex_server.Info())
            return info
        except Exception as e:
            log.error("get server info failed: %s", e)
            return None
    
    @update_last_ack_time
    def get_count(self):
        return self.call(goods.Count())
    
    @update_last_ack_time
    def get_category_list(self):
        return self.call(goods.CategoryList())
    
    @update_last_ack_time
    def get_Detail(self, start=0, count=100):
        return self.call(goods.Detail(start, count))
    
    @update_last_ack_time
    def get_quotes_single(self, category: EX_CATEGORY, code):
        return self.call(goods.QuotesSingle(category, code))
    
    @update_last_ack_time
    def get_quotes(self, code_list: list[tuple[EX_CATEGORY, str]], code):
        if code is not None:
            code_list = [(code_list, code)]
        elif (isinstance(code_list, list) or isinstance(code_list, tuple))\
                and len(code_list) == 2 and type(code_list[0]) is int:
            code_list = [code_list]

        return self.call(goods.Quotes(code_list))
    
    @update_last_ack_time
    def get_kline(self, category: EX_CATEGORY, code: str, period: PERIOD, start: int = 0, count: int = 800, times: int = 1):
        return self.call(goods.K_Line(category, code, period, times, start, count))
    
    @update_last_ack_time
    def get_history_transaction(self, category: EX_CATEGORY, code: str, date: date):
        return self.call(goods.HistoryTransaction(category, code, date))
    
    @update_last_ack_time
    def get_table(self):
        start = 0
        str = ''
        while True:
            _, count, context = self.call(goods.Table(start))
            start += count
            str += context
            if count <= 0:
                break
        return str
    
    @update_last_ack_time
    def get_table_detail(self):
        start = 0
        str = ''
        while True:
            _, count, context = self.call(goods.TableDetail(start))
            start += count
            str += context
            if count <= 0:
                break
        return str

    @update_last_ack_time
    def get_futures_quotes_list(self, category: EX_CATEGORY, start: int = 0, count: int = 100):
        return self.call(goods.Futures_QuotesList(category, start, count))
    
    @update_last_ack_time
    def get_futures_quotes(self, code_list: list[tuple[EX_CATEGORY, str]], code = None):
        if code is not None:
            code_list = [(code_list, code)]
        elif (isinstance(code_list, list) or isinstance(code_list, tuple))\
                and len(code_list) == 2 and type(code_list[0]) is int:
            code_list = [code_list]
        return self.call(goods.Futures_Quotes(code_list))
    
    @update_last_ack_time
    def get_tick_chart(self, category: EX_CATEGORY, code: str):
        return self.call(goods.TickChart(category, code))
    
    @update_last_ack_time
    def get_history_tick_chart(self, category: EX_CATEGORY, code: str, date: date):
        return self.call(goods.HistoryTickChart(category, code, date))
    
    @update_last_ack_time
    def get_chart_sampling(self, category: EX_CATEGORY, code: str):
        return self.call(goods.ChartSampling(category, code))