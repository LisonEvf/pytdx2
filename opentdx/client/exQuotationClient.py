from datetime import date

from opentdx.parser.ex_quotation import file, goods

from .baseStockClient import BaseStockClient, update_last_ack_time, _paginate, _normalize_code_list
from opentdx.parser.ex_quotation import server as ex_server
from opentdx.const import EX_MARKET, PERIOD, SORT_TYPE, ex_hosts
from opentdx.utils.log import log

class exQuotationClient(BaseStockClient):
    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = ex_hosts

    def login(self, show_info=False) -> bool:
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
    def get_count(self) -> int:
        return self.call(goods.Count())

    @update_last_ack_time
    def get_category_list(self) -> list[dict]:
        return self.call(goods.CategoryList())

    @update_last_ack_time
    def get_list(self, start: int = 0, count: int = 2000) -> list[dict]:
        return self.call(goods.List(start, count))

    @update_last_ack_time
    def get_quotes_list(self, market: EX_MARKET, start: int = 0, count: int = 100, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False) -> list[dict]:
        return _paginate(
            lambda s, c: self.call(goods.QuotesList(market, s, c, sortType, reverse)),
            100, count,
        )

    @update_last_ack_time
    def get_quotes_single(self, market: EX_MARKET, code) -> dict:
        return self.call(goods.QuotesSingle(market, code))

    @update_last_ack_time
    def get_quotes(self, code_list, code=None) -> list[dict]:
        code_list = _normalize_code_list(code_list, code)
        return self.call(goods.Quotes(code_list))

    @update_last_ack_time
    def get_quotes2(self, code_list, code=None) -> list[dict]:
        code_list = _normalize_code_list(code_list, code)
        return self.call(goods.Quotes2(code_list))

    @update_last_ack_time
    def get_kline(self, market: EX_MARKET, code: str, period: PERIOD, start: int = 0, count: int = 800, times: int = 1) -> list[dict]:
        return self.call(goods.K_Line(market, code, period, times, start, count))

    @update_last_ack_time
    def get_history_transaction(self, market: EX_MARKET, code: str, date: date) -> list[dict]:
        return self.call(goods.HistoryTransaction(market, code, date))

    @update_last_ack_time
    def get_table(self):
        start = 0
        result = ''
        while True:
            _, count, context = self.call(goods.Table(start))
            start += count
            result += context
            if count <= 0:
                break
        return result

    @update_last_ack_time
    def get_table_detail(self):
        start = 0
        result = ''
        while True:
            _, count, context = self.call(goods.TableDetail(start))
            start += count
            result += context
            if count <= 0:
                break
        return result

    @update_last_ack_time
    def get_tick_chart(self, market: EX_MARKET, code: str, date: date = None) -> list[dict]:
        if date is None:
            return self.call(goods.TickChart(market, code))
        else:
            return self.call(goods.HistoryTickChart(market, code, date))

    @update_last_ack_time
    def get_chart_sampling(self, market: EX_MARKET, code: str) -> list[float]:
        return self.call(goods.ChartSampling(market, code))

    @update_last_ack_time
    def download_file(self, filename: str, filesize=0, report_hook=None):
        return super().download_file(file.Download, filename, filesize, report_hook)
