from datetime import date
import math
from typing import override
from client.baseStockClient import BaseStockClient, update_last_ack_time
from utils.block_reader import BlockReader, BlockReader_TYPE_FLAT
from const import BLOCK_FILE_TYPE, CATEGORY, FILTER_TYPE, PERIOD, MARKET, SORT_TYPE, main_hosts
from parser.quotation import file, stock, server, company_info
from utils.log import log

class QuotationClient(BaseStockClient):
    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = main_hosts

    def login(self, show_info=False):
        try:
            info = self.call(server.Login())
            if show_info:
                print(info)
            
            # self.call(remote.Notice())
            return True
        except Exception as e:
            log.error("login failed: %s", e)
            return False

    @override
    def doHeartBeat(self):
        result = self.call(server.HeartBeat())
        if self.heartbeat:
            self.heartbeat_thread.update_last_ack_time()

        return result
        
    
    def quotes_adjustment(self, quotes_list):
        for quotes in quotes_list:
            for item in ['open', 'high', 'low', 'price', 'pre_close', 'neg_price']:
                quotes[item] /= 100
            
            quotes['open_amount'] *= 100
            quotes['rise_speed'] = f'{(quotes["rise_speed"] / 100):.2f}%'
            for bid in quotes['handicap']['bid']:
                bid['price'] = bid['price']/100
            for ask in quotes['handicap']['ask']:
                ask['price'] = ask['price']/100
                
        return quotes_list
    
    @update_last_ack_time
    def get_count(self, market: MARKET):
        return self.call(stock.Count(market))


    @update_last_ack_time
    def get_list(self, market: MARKET, start = 0, count = 0):
        MAX_LIST_COUNT = 1600
        results = []
        # 如果 count 为 0，则设置 remaining 为无穷大，表示获取所有数据
        remaining = count if count != 0 else float('inf')
        while remaining > 0:
            req_count = min(remaining, MAX_LIST_COUNT)
            part = self.call(stock.List(market, start, req_count))
            results.extend(part)
            if len(part) < req_count:
                break
            remaining -= len(part)
            start += len(part)
        return results

    @update_last_ack_time
    def get_vol_profile(self, market: MARKET, code: str):
        quotes_list = self.call(stock.VolumeProfile(market, code))
        return self.quotes_adjustment(quotes_list)
    
    @update_last_ack_time
    def get_index_momentum(self, market: MARKET, code: str):
        return self.call(stock.IndexMomentum(market, code))

    @update_last_ack_time
    def get_index_info(self, all_stock, code=None):
        if code is not None:
            all_stock = [(all_stock, code)]
        elif (isinstance(all_stock, list) or isinstance(all_stock, tuple))\
                and len(all_stock) == 2 and type(all_stock[0]) is int:
            all_stock = [all_stock]
        
        index_infos = []
        for market, code in all_stock:
            index_info = self.call(stock.IndexInfo(market, code))
            for item in ['diff', 'pre_close', 'close', 'open', 'high', 'low']:
                index_info[item] /= 100
            index_infos.append(index_info)

        return index_infos
    
    @update_last_ack_time
    def get_kline(self, market: MARKET, code: str, period: PERIOD, start = 0, count = 800, times: int = 1):
        MAX_KLINE_COUNT = 800
        bars = []
        while len(bars) < count:
            part = self.call(stock.K_Line(market, code, period, times, start + len(bars), min((count - len(bars)), MAX_KLINE_COUNT)))
            if not part:
                break
            bars = [*part, *bars]
        
        for bar in bars:
            bar['open'] = bar['open']/1000
            bar['close'] = bar['close']/1000
            bar['high'] = bar['high']/1000
            bar['low'] = bar['low']/1000

        return bars
    
    @update_last_ack_time
    def get_tick_chart(self, market: MARKET, code: str, start: int = 0, count: int = 0xba00):
        data = self.call(stock.TickChart(market, code, start, count))
        for item in data:
            item['price'] /= 100
            item['avg'] /= 10000
        return data
    
    @update_last_ack_time
    def get_stock_quotes_details(self, code_list: MARKET | list[tuple[MARKET, str]], code=None):
        if code is not None:
            code_list = [(code_list, code)]
        elif (isinstance(code_list, list) or isinstance(code_list, tuple))\
                and len(code_list) == 2 and type(code_list[0]) is int:
            code_list = [code_list]
        
        quotes_list = self.call(stock.QuotesDetail(code_list))
        return self.quotes_adjustment(quotes_list)
    
    @update_last_ack_time
    def get_stock_top_board(self, category: CATEGORY):
        boards = self.call(stock.TopBoard(category))
        for _, board in boards.items():
            for item in board:
                item['price'] = f'{item["price"]:.2f}'
        return boards
    
    @update_last_ack_time
    def get_stock_quotes_list(self, category: CATEGORY, start:int = 0, count: int = 80, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False, filter: list[FILTER_TYPE] = []):
        MAX_QUOTE_COUNT = 80
        results = []
        # 如果 count 为 0，则设置 remaining 为无穷大，表示获取所有数据
        remaining = count if count != 0 else float('inf')
        while remaining > 0:
            req_count = min(remaining, MAX_QUOTE_COUNT)
            part = self.call(stock.QuotesList(category, start, req_count, sortType, reverse, filter))
            results.extend(part)
            if len(part) < req_count:
                break
            remaining -= len(part)
            start += len(part)
            
        for quotes in results:
            quotes['short_turnover'] = f'{(quotes['short_turnover'] / 100):.2f}%'
            quotes['opening_rush'] = f'{(quotes['opening_rush'] / 100):.2f}%'
            quotes['vol_rise_speed'] = f'{(quotes['vol_rise_speed']):.2f}%'
            quotes['depth'] = f'{(quotes["depth"]):.2f}%'

        return self.quotes_adjustment(results)

    @update_last_ack_time
    def get_quotes(self, all_stock, code=None):
        if code is not None:
            all_stock = [(all_stock, code)]
        elif (isinstance(all_stock, list) or isinstance(all_stock, tuple))\
                and len(all_stock) == 2 and type(all_stock[0]) is int:
            all_stock = [all_stock]

        quotes_list = self.call(stock.Quotes(all_stock))

        for quotes in quotes_list:
            quotes['short_turnover'] = f'{(quotes['short_turnover'] / 100):.2f}%'
            quotes['opening_rush'] = f'{(quotes['opening_rush'] / 100):.2f}%'
            quotes['vol_rise_speed'] = f'{(quotes['vol_rise_speed']):.2f}%'
            quotes['depth'] = f'{(quotes["depth"]):.2f}%'

        return self.quotes_adjustment(quotes_list)
    
    @update_last_ack_time
    def get_unusual(self, market: MARKET, start: int = 0, count: int = 0):
        MAX_UNUSUAL_COUNT = 600
        results = []
        # 如果 count 为 0，则设置 remaining 为无穷大，表示获取所有数据
        remaining = count if count != 0 else float('inf')
        while remaining > 0:
            req_count = min(remaining, MAX_UNUSUAL_COUNT)
            part = self.call(stock.Unusual(market, start, req_count))
            results.extend(part)
            if len(part) < req_count:
                break
            remaining -= len(part)
            start += len(part)
        return results
    
    @update_last_ack_time
    def get_auction(self, market: MARKET, code: str):
        return self.call(stock.Auction(market, code))
    
    @update_last_ack_time
    def get_history_orders(self, market: MARKET, code: str, date: date):
        data = self.call(stock.HistoryOrders(market, code, date))
        for item in data:
            item['price'] = item['price'] / 100
        return data

    @update_last_ack_time
    def get_history_transaction(self, market: MARKET, code: str, date: date):
        MAX_TRANSACTION_COUNT = 2000
        start = 0
        transaction = []
        while True:
            part = self.call(stock.HistoryTransaction(market, code, date, start, MAX_TRANSACTION_COUNT))
            if not part:
                break
            transaction = [*part, *transaction]
            if len(part) < MAX_TRANSACTION_COUNT:
                break
            start = start + len(part)
        for item in transaction:
            item['price'] = item['price'] / 100
        return transaction

    @update_last_ack_time
    def get_transaction(self, market: MARKET, code: str):
        MAX_TRANSACTION_COUNT = 1800
        start = 0
        transaction = []
        while True:
            part = self.call(stock.Transaction(market, code, start, MAX_TRANSACTION_COUNT))
            if not part:
                break
            transaction = [*part, *transaction]
            if len(part) < MAX_TRANSACTION_COUNT:
                break
            start = start + len(part)
        for item in transaction:
            item['price'] = item['price'] / 100
        return transaction

    @update_last_ack_time
    def get_history_transaction_with_trans(self, market: MARKET, code: str, date: date):
        MAX_TRANSACTION_COUNT = 1800
        start = 0
        transaction = []
        while True:
            part = self.call(stock.HistoryTransactionWithTrans(market, code, date, start, MAX_TRANSACTION_COUNT))
            if not part:
                break
            transaction = [*part, *transaction]
            if len(part) < MAX_TRANSACTION_COUNT:
                break
            start = start + len(part)
        for item in transaction:
            item['price'] = item['price'] / 100
        return transaction
    
    @update_last_ack_time
    def get_history_tick_chart(self, market: MARKET, code: str, date: date):
        data = self.call(stock.HistoryTickChart(market, code, date))
        for item in data:
            item['price'] = item['price'] / 100
            item['avg'] = item['avg'] / 10000
        return data
    
    @update_last_ack_time
    def get_chart_sampling(self, market: MARKET, code: str):
        return self.call(stock.ChartSampling(market, code)) 

    @update_last_ack_time
    def get_company_info(self, market: MARKET, code: str):
        category = self.call(company_info.Category(market, code))

        info = []
        for part in category:
            content = self.call(company_info.Content(market, code, part['filename'], part['start'], part['length']))
            info.append({
                'name': part['name'],
                'content': content['content'],
            })

        xdxr = self.call(company_info.XDXR(market, code))
        if xdxr:
            info.append({
                'name': '除权分红',
                'content': xdxr,
            })

        finance = self.call(company_info.Finance(market, code))
        if finance:
            info.append({
                'name': '财报',
                'content': finance,
            })
        return info

    @update_last_ack_time
    def get_block_file(self, block_file_type: BLOCK_FILE_TYPE):
        try:
            meta = self.call(file.Meta(block_file_type.value))
        except Exception as e:
            log.error(e)
            return None

        if not meta:
            return None

        size = meta['size']
        one_chunk = 0x7530

        file_content = bytearray()
        for seg in range(math.ceil(size / one_chunk)):
            start = seg * one_chunk
            piece_data = self.call(file.Block(block_file_type, start, one_chunk))["data"]
            file_content.extend(piece_data)

        return BlockReader().get_data(file_content, BlockReader_TYPE_FLAT)

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
    
    @update_last_ack_time
    def get_table_file(self, filename: str):
        '''
        获取表格文件
        :param filename: 表格文件名
        :return: 文件内容字符串
        '''
        file_content = self.download_file(filename).decode("gbk")
        lines = [line.strip() for line in file_content.split('\n') if line.strip()]
        # 将数据解析为列表
        data = []
        for line in lines:
            # 按竖线分割
            fields = line.split('|')
            data.append(fields)
        return data
    
    @update_last_ack_time
    def get_csv_file(self, filename: str):
        '''
        获取表格文件
        :param filename: 表格文件名
        :return: 文件内容字符串
        '''
        file_content = self.download_file(filename).decode("gbk")
        lines = [line.strip() for line in file_content.split('\n') if line.strip()]
        # 将数据解析为列表
        data = []
        for line in lines:
            # 按竖线分割
            fields = line.split(',')
            data.append(fields)
        return data
