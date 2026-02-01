from datetime import date
import math
from typing import override
from client.baseStockClient import BaseStockClient, update_last_ack_time
from utils.block_reader import BlockReader, BlockReader_TYPE_FLAT
from const import BLOCK_FILE_TYPE, CATEGORY, PERIOD, MARKET, main_hosts
from parser.quotation import file, stock, server, company_info
from utils.log import log

class QuotationClient(BaseStockClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        self.call(server.HeartBeat())
    
    @update_last_ack_time
    def get_security_count(self, market: MARKET):
        '''
        获取股票数量
        :param market: MARKET

        :return count
        '''
        return self.call(stock.Count(market))

    @update_last_ack_time
    def get_security_list(self, market: MARKET, start = 0, count = 1600):
        '''
        获取股票列表
        :param market: MARKET
        :param start?: 起始位置
        :param count?: 获取数量
        :return: [{
            'code': str(code),
            'name': str(name),
            'pre_close': int(pre_close),
            'vol': int(vol),
        }, ...]
        '''
        MAX_LIST_COUNT = 1600
        security_list = []
        while count > 0:
            part = self.call(stock.List(market, start, min(count, MAX_LIST_COUNT)))
            security_list.extend(part)
            count -= len(part)
            start += len(part)
        return security_list

    @update_last_ack_time
    def get_index_info(self, all_stock, code=None):
        '''
        获取指数概况
        支持三种形式的参数
        get_index_info(market, code )
        get_index_info((market, code))
        get_index_info([(market1, code1), (market2, code2)] )
        :param all_stock （market, code) 的数组
        :param code{optional} code to query
        :return:[{
            'market': MARKET,
            'code': str(code),
            'open': float(open),
            'high': float(high),
            'low': float(low),
            'close': float(close),
            'pre_close': float(pre_close),
            'diff': float(diff),
            'vol': int(vol),
            'amount': int(amount),
            'up_count': int(up_count),
            'down_count': int(down_count),
            'active': int(active),
        }, ...]
        '''
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
    def get_KLine_data(self, market: MARKET, code: str, period: PERIOD, start = 0, count = 800):
        '''
        获取K线数据
        :param market: MARKET
        :param code: 股票代码
        :param period: 周期
        :param start: 起始位置
        :param count: 获取数量
        
        :return [{datetime: , open: , close: , high: , low: , vol: , amount: , upCount?: , downCount?: }, ...]
        '''
        MAX_KLINE_COUNT = 800
        bars = []
        while len(bars) < count:
            part = self.call(stock.K_Line(market, code, period, start + len(bars), min((count - len(bars)), MAX_KLINE_COUNT)))
            bars = [*part, *bars]
        
        for bar in bars:
            bar['open'] = bar['open']/1000
            bar['close'] = bar['close']/1000
            bar['high'] = bar['high']/1000
            bar['low'] = bar['low']/1000

        return bars
    
    @update_last_ack_time
    def get_security_quotes_details(self, all_stock, code=None):
        """
        获取详细行情
        支持三种形式的参数
        get_security_quotes(market, code )
        get_security_quotes((market, code))
        get_security_quotes([(market1, code1), (market2, code2)] )
        :param all_stock （market, code) 的数组
        :param code{optional} code to query
        :return:[{
            'market': MARKET, # 市场
            'code': str(code), # 股票代码
            'name': str(name), # 股票名称
            'open': float(open), # 今开
            'high': float(high), # 最高
            'low': float(low), # 最低
            'price': float(price), # 最新价
            'pre_close': float(pre_close), # 昨收
            'server_time': str(server_time), # 服务器时间
            'neg_price': int(neg_price), # 负数最新价
            'vol': int(vol), # 总量
            'cur_vol': int(cur_vol), # 现量
            'amount': int(amount), # 总金额
            's_vol': int(s_vol), # 内盘
            'b_vol': int(b_vol), # 外盘
            's_amount': int(s_amount), 
            'open_amount': int(open_amount), # 开盘金额
            'handicap': {
                'bid': [{'price': float(price), 'vol': int(vol)}, ...],
                'ask': [{'price': float(price), 'vol': int(vol)}, ...],
            }, # 五档盘口
            'rise_speed': str(rise_speed_percent), # 涨速
            'active1': int(active), # 活跃度
        }, ...]
        """
        if code is not None:
            all_stock = [(all_stock, code)]
        elif (isinstance(all_stock, list) or isinstance(all_stock, tuple))\
                and len(all_stock) == 2 and type(all_stock[0]) is int:
            all_stock = [all_stock]

        
        quote_details = self.call(stock.QuotesDetail(all_stock))
        for quote in quote_details:
            for item in ['open', 'high', 'low', 'price', 'pre_close', 'neg_price']:
                quote[item] /= 100
            
            quote['open_amount'] *= 100
            quote['rise_speed'] = f'{(quote["rise_speed"] / 100):.2f}%'
            for bid in quote['handicap']['bid']:
                bid['price'] = bid['price']/100
            for ask in quote['handicap']['ask']:
                ask['price'] = ask['price']/100
        return quote_details
    
    @update_last_ack_time
    def get_top_stock_board(self, category: CATEGORY):
        '''
        获取行情全景
        :param category: CATEGORY
        :return: {
            'increase': [{
                'market': MARKET,
                'code': str(code),
                'price': float(price),
                'value': float(increase),
            }, ...], # 涨幅榜
            'decrease': [{
                'market': MARKET,
                'code': str(code),
                'name': str(name),
                'price': float(price),
                'value': float(decrease),
            }, ...], # 跌幅榜
            'amplitude': [{
                'market': MARKET,
                'code': str(code),
                'name': str(name),
                'price': float(price),
                'value': float(amplitude),
            }, ...], # 振幅榜
            'rise_speed': [{
                'market': MARKET,
                'code': str(code),
                'name': str(name),
                'price': float(price),
                'value': float(rise_speed),
            }, ...], # 涨速榜
            'fall_speed': [{
                'market': MARKET,
                'code': str(code),
                'name': str(name),
                'price': float(price),
                'value': float(fall_speed),
            }, ...], # 跌速榜
            'vol_ratio': [{
                'market': MARKET,
                'code': str(code),
                'name': str(name),
                'price': float(price),
                'value': float(vol_ratio),
            }, ...], # 量比榜
            'pos_commission_ratio': [{
                'market': MARKET,
                'code': str(code),
                'name': str(name),
                'price': float(price),
                'value': float(pos_commission_ratio),
            }, ...],  # 委比正序
            'neg_commission_ratio': [{
                'market': MARKET,
                'code': str(code),
                'name': str(name),
                'price': float(price),
                'value': float(neg_commission_ratio),
            }, ...], # 委比倒序
            'turnover': [{
                'market': MARKET,
                'code': str(code),
                'name': str(name),
                'price': float(price),
                'value': float(turnover),
            }, ...] # 换手率榜
        }
        '''
        boards = self.call(stock.TopStocksBoard(category))
        for _, board in boards.items():
            for item in board:
                item['price'] = f'{item["price"]:.2f}'
        return boards
    
    @update_last_ack_time
    def get_security_quotes_by_category(self, category: CATEGORY, start:int = 0, count: int = 0x50):
        '''
        获取行情列表
        :param category: CATEGORY
        :param start: 起始位置
        :param count: 获取数量
        :return: [{
            'market': MARKET, # 市场
            'code': str(code), # 股票代码
            'name': str(name), # 股票名称
            'open': float(open), # 今开
            'high': float(high), # 最高
            'low': float(low), # 最低
            'price': float(price), # 最新价
            'pre_close': float(pre_close), # 昨收
            'server_time': str(server_time), # 服务器时间
            'neg_price': int(neg_price), # 负数最新价
            'vol': int(vol), # 总量
            'cur_vol': int(cur_vol), # 现量
            'amount': int(amount), # 总金额
            's_vol': int(s_vol), # 内盘
            'b_vol': int(b_vol), # 外盘
            's_amount': int(s_amount),
            'open_amount': int(open_amount), # 开盘金额
            'handicap': {
                'bid': [{'price': float(price), 'vol': int(vol)}, ...],
                'ask': [{'price': float(price), 'vol': int(vol)}, ...],
            }, # 一档盘口
            'rise_speed': str(rise_speed_percent), # 涨速
            'short_turnover': str(short_turnover_percent), # 短换手
            'min2_amount': int(min2_amount), # 两分钟成交额
            'opening_rush': str(opening_rush_percent), # 开盘抢筹
            'vol_rise_speed': str(vol_rise_speed_percent), # 量涨速
            'depth': str(depth_percent), # 委比
            'active1': int(active), # 活跃度
        }, ...]
        '''
        MAX_QUOTE_COUNT = 80
        quotes = []
        while count > len(quotes):
            quotes.extend(self.call(stock.QuotesList(category, start + len(quotes), min(count - len(quotes), MAX_QUOTE_COUNT))))
            
        for quote in quotes:
            
            for item in ['open', 'high', 'low', 'price', 'pre_close', 'neg_price']:
                quote[item] /= 100

            for item in ['rise_speed', 'short_turnover', 'opening_rush']:
                quote[item] = f'{(quote[item] / 100):.2f}%'

            quote['vol_rise_speed'] = f'{(quote["vol_rise_speed"]):.2f}%'
            quote['depth'] = f'{(quote["depth"]):.2f}%'
            
            for bid in quote['handicap']['bid']:
                bid['price'] = bid['price']/100
            for ask in quote['handicap']['ask']:
                ask['price'] = ask['price']/100
        return quotes

    @update_last_ack_time
    def get_security_quotes(self, all_stock, code=None):
        '''
        获取简略行情
        支持三种形式的参数
        get_security_quotes(market, code )
        get_security_quotes((market, code))
        get_security_quotes([(market1, code1), (market2, code2)] )
        :param all_stock （market, code) 的数组
        :param code{optional} code to query

        :return: [{
            'market': MARKET, # 市场
            'code': str(code), # 股票代码
            'name': str(name), # 股票名称
            'open': float(open), # 今开
            'high': float(high), # 最高
            'low': float(low), # 最低
            'price': float(price), # 最新价
            'pre_close': float(pre_close), # 昨收
            'server_time': str(server_time), # 服务器时间
            'neg_price': int(neg_price), # 负数最新价
            'vol': int(vol), # 总成交量
            'cur_vol': int(cur_vol), # 当前成交量
            'amount': int(amount), # 总成交额
            's_vol': int(s_vol), # 内盘
            'b_vol': int(b_vol), # 外盘
            's_amount': int(s_amount),
            'open_amount': int(open_amount), # 开盘金额
            'handicap': {
                'bid': [{'price': float(price), 'vol': int(vol)}, ...],
                'ask': [{'price': float(price), 'vol': int(vol)}, ...],
            }, # 一档盘口
            'rise_speed': str(rise_speed_percent), # 涨速
            'short_turnover': str(short_turnover_percent), # 短换手
            'min2_amount': int(min2_amount), # 两分钟成交额
            'opening_rush': str(opening_rush_percent), # 开盘抢筹
            'vol_rise_speed': str(vol_rise_speed_percent), # 量涨速
            'depth': str(depth_percent), # 委比
            'active1': int(active), # 活跃度
        }, ...]
        '''
        if code is not None:
            all_stock = [(all_stock, code)]
        elif (isinstance(all_stock, list) or isinstance(all_stock, tuple))\
                and len(all_stock) == 2 and type(all_stock[0]) is int:
            all_stock = [all_stock]

        quotes = self.call(stock.Quotes(all_stock))
        for quote in quotes:
            for item in ['open', 'high', 'low', 'price', 'pre_close', 'neg_price']:
                quote[item] /= 100

            for item in ['rise_speed', 'short_turnover', 'opening_rush']:
                quote[item] = f'{(quote[item] / 100):.2f}%'

            quote['vol_rise_speed'] = f'{(quote["vol_rise_speed"]):.2f}%'
            quote['depth'] = f'{(quote["depth"]):.2f}%'

            for bid in quote['handicap']['bid']:
                bid['price'] = bid['price']/100
            for ask in quote['handicap']['ask']:
                ask['price'] = ask['price']/100

        return quotes
    
    @update_last_ack_time
    def get_unusual(self, market: MARKET, start: int = 0, count: int = 0):
        '''
        获取异动股
        :param market: MARKET
        :param start: 起始位置
        :param count: 获取数量
        :return: [{
            'index': int(index),
            'market': MARKET,
            'code': str(code),
            'time': str(time),
            'desc': str(desc),
            'value': str(value),
            }, ...]
        '''
        MAX_UNUSUAL_COUNT = 600
        unusual_stocks = []
        while True:
            part = self.call(stock.Unusual(market, start, min(count, MAX_UNUSUAL_COUNT) if count > 0 else MAX_UNUSUAL_COUNT))
            if not part:
                break
            unusual_stocks.extend(part)
            start += len(part)
            if count == 0:
                continue
            count -= len(part)
            if len(part) >= count:
                break
        return unusual_stocks
    
    
    @update_last_ack_time
    def get_history_orders(self, market: MARKET, code: str, date: date):
        '''
        获取历史分时行情
        :param market: MARKET
        :param code: 股票代码
        :param date: 日期
        :return: {
            'pre_close': float(pre_close),
            'orders': [{
                'price': float(price),
                'vol': int(vol),
            }, ...]
        }
        '''
        data = self.call(stock.HistoryOrders(market, code, date))
        for item in data['orders']:
            item['price'] = item['price'] / 100
        return data

    @update_last_ack_time
    def get_history_transaction(self, market: MARKET, code: str, date: date):
        '''
        获取历史分时成交
        :param market: MARKET
        :param code: 股票代码
        :param date: 日期
        :return: [{
            'time': str(time),
            'price': float(price),
            'vol': int(vol),
            'action': str('SELL'|'BUY'|'NEUTRAL'),
        }, ...]
        '''
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
        '''
        获取分时成交
        :param market: MARKET
        :param code: 股票代码
        :return: [{
            'time': str(time),
            'price': float(price),
            'vol': int(vol),
            'trans': int(trans),
            'action': str('SELL'|'BUY'|'NEUTRAL'),
        }, ...]
        '''
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
    
    def get_chart_sampling(self, market: MARKET, code: str):
        '''
        获取分时图缩略数据
        :param market: MARKET
        :param code: 股票代码
        :return: {
            'prices': [float(price), ...],
            'vols': [int(vol), ...],
        }
        '''
        return self.call(stock.ChartSampling(market, code)) 
    
    

    @update_last_ack_time
    def get_company_info(self, market: MARKET, code: str):
        '''
        获取公司信息
        :param market: MARKET
        :param code: 股票代码
        :return: [{
            'name': str(name),
            'content': str(content),
        }, ...]
        '''
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
        '''
        获取板块信息
        :param block_file_type: BLOCK_FILE_TYPE
        :return: [{
            'block_name': str(block_name),
            'stocks': [str(code), ...],
        }, ...]
        '''
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
