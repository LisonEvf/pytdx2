from datetime import date

from opentdx.parser import ex_quotation

from .baseStockClient import BaseStockClient, update_last_ack_time, _paginate, _normalize_code_list
from .commonClientMixin import CommonClientMixin
from opentdx.const import EX_MARKET, PERIOD, SORT_TYPE, ex_hosts, mac_ex_hosts
from opentdx.utils.log import log

class exQuotationClient(BaseStockClient, CommonClientMixin):
    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = ex_hosts
        self._sp_mode_enabled = False

    def sp(self, hosts=mac_ex_hosts):
        """启动sp模式,支持mac协议调用.

        Args:
            hosts (list of str): List of hosts to use.

        Returns:
            self
        """
        self.hosts = hosts
        self._sp_mode_enabled = True
        return self

    def login(self, show_info=False) -> bool:
        try:
            info = self.call(ex_quotation.Login())
            if show_info:
                log.info("login info: %s", info)
            return True
        except Exception as e:
            log.error("login failed: %s", e)
            return False

    def server_info(self):
        try:
            info = self.call(ex_quotation.ServerInfo())
            return info
        except Exception as e:
            log.error("get server info failed: %s", e)
            return None

    @update_last_ack_time
    def get_count(self) -> int:
        return self.call(ex_quotation.Count())

    @update_last_ack_time
    def get_category_list(self) -> list[dict]:
        return self.call(ex_quotation.CategoryList())

    @update_last_ack_time
    def get_list(self, start: int = 0, count: int = 2000) -> list[dict]:
        return self.call(ex_quotation.List(start, count))

    @update_last_ack_time
    def get_quotes_list(self, market: EX_MARKET, start: int = 0, count: int = 100, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False) -> list[dict]:
        return _paginate(
            lambda s, c: self.call(ex_quotation.QuotesList(market, s, c, sortType, reverse)),
            100, count, start,
        )

    @update_last_ack_time
    def get_quotes_single(self, market: EX_MARKET, code) -> dict:
        return self.call(ex_quotation.QuotesSingle(market, code))

    @update_last_ack_time
    def get_quotes(self, code_list, code=None) -> list[dict]:
        code_list = _normalize_code_list(code_list, code)
        return self.call(ex_quotation.Quotes(code_list))

    @update_last_ack_time
    def get_quotes2(self, code_list, code=None) -> list[dict]:
        code_list = _normalize_code_list(code_list, code)
        return self.call(ex_quotation.Quotes2(code_list))

    @update_last_ack_time
    def get_kline(self, market: EX_MARKET, code: str, period: PERIOD, start: int = 0, count: int = 800, times: int = 1) -> list[dict]:
        return self.call(ex_quotation.K_Line(market, code, period, times, start, count))

    @update_last_ack_time
    def get_history_transaction(self, market: EX_MARKET, code: str, date: date) -> list[dict]:
        return self.call(ex_quotation.HistoryTransaction(market, code, date))

    @update_last_ack_time
    def get_table(self):
        start = 0
        result = ''
        while True:
            _, count, context = self.call(ex_quotation.Table(start))
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
            _, count, context = self.call(ex_quotation.TableDetail(start))
            start += count
            result += context
            if count <= 0:
                break
        return result

    @update_last_ack_time
    def get_tick_chart(self, market: EX_MARKET, code: str, date: date = None) -> list[dict]:
        if date is None:
            return self.call(ex_quotation.TickChart(market, code))
        else:
            return self.call(ex_quotation.HistoryTickChart(market, code, date))

    @update_last_ack_time
    def get_chart_sampling(self, market: EX_MARKET, code: str) -> list[float]:
        return self.call(ex_quotation.ChartSampling(market, code))

    @update_last_ack_time
    def download_file(self, filename: str, filesize=0, report_hook=None):
        return super().download_file(ex_quotation.FileDownload, filename, filesize, report_hook)
