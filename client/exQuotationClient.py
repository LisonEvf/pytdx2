from datetime import date

from parser.ex_quotation import file, goods

from .baseStockClient import BaseStockClient, update_last_ack_time
from parser.ex_quotation import server as ex_server
from const import EX_CATEGORY, PERIOD, SORT_TYPE, ex_hosts
from utils.log import log

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
    def get_quotes_list(self, category: EX_CATEGORY, start: int = 0, count: int = 100, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False) -> list[dict]:
        MAX_QUOTE_COUNT = 100
        results = []
        # 如果 count 为 0，则设置 remaining 为无穷大，表示获取所有数据
        remaining = count if count != 0 else float('inf')
        while remaining > 0:
            req_count = min(remaining, MAX_QUOTE_COUNT)
            part = self.call(goods.QuotesList(category, start, req_count, sortType, reverse))
            results.extend(part)
            if len(part) < req_count:
                break
            remaining -= len(part)
            start += len(part)

        return results
    
    @update_last_ack_time
    def get_quotes_single(self, category: EX_CATEGORY, code) -> dict:
        return self.call(goods.QuotesSingle(category, code))
    
    @update_last_ack_time
    def get_quotes(self, code_list: list[tuple[EX_CATEGORY, str]], code = None) -> list[dict]:
        if code is not None:
            code_list = [(code_list, code)]
        elif (isinstance(code_list, list) or isinstance(code_list, tuple))\
                and len(code_list) == 2 and type(code_list[0]) is int:
            code_list = [code_list]
        return self.call(goods.Quotes(code_list))
    
    @update_last_ack_time
    def get_quotes2(self, code_list: list[tuple[EX_CATEGORY, str]], code) -> list[dict]:
        if code is not None:
            code_list = [(code_list, code)]
        elif (isinstance(code_list, list) or isinstance(code_list, tuple))\
                and len(code_list) == 2 and type(code_list[0]) is int:
            code_list = [code_list]

        return self.call(goods.Quotes2(code_list))
    
    @update_last_ack_time
    def get_kline(self, category: EX_CATEGORY, code: str, period: PERIOD, start: int = 0, count: int = 800, times: int = 1) -> list[dict]:
        return self.call(goods.K_Line(category, code, period, times, start, count))
    
    @update_last_ack_time
    def get_history_transaction(self, category: EX_CATEGORY, code: str, date: date) -> list[dict]:
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
    def get_tick_chart(self, category: EX_CATEGORY, code: str, date: date = None) -> list[dict]:
        if date is None:
            return self.call(goods.TickChart(category, code))
        else:
            return self.call(goods.HistoryTickChart(category, code, date))
    
    @update_last_ack_time
    def get_chart_sampling(self, category: EX_CATEGORY, code: str) -> list[float]:
        return self.call(goods.ChartSampling(category, code))

    @update_last_ack_time
    def download_file(self, filename: str, filesize=0, report_hook=None):
        '''
        获取报告文件
        :param filename: 报告文件名
        :param filesize: 报告文件大小，如果不清楚可以传0
        :param report_hook: 下载进度回调函数，函数原型 report_hook(downloaded_size, total_size)
        :return: 文件内容字符串
        '''
        file_content = bytearray(filesize)
        current_downloaded_size = 0
        get_zero_length_package_times = 0
        while current_downloaded_size < filesize or filesize == 0:
            response = self.call(file.Download(filename, current_downloaded_size))
            if response["size"] > 0:
                current_downloaded_size = current_downloaded_size + response["size"]
                file_content.extend(response["data"])
                if report_hook is not None:
                    report_hook(current_downloaded_size, filesize)
            else:
                get_zero_length_package_times = get_zero_length_package_times + 1
                if filesize == 0:
                    break
                elif get_zero_length_package_times > 2:
                    break
        return file_content