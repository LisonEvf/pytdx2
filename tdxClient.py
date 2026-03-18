

from datetime import date
import pandas as pd

from client.exQuotationClient import exQuotationClient
from client.quotationClient import QuotationClient
from const import BLOCK_FILE_TYPE, CATEGORY, EX_CATEGORY, MARKET, PERIOD

class TdxClient:
    def __enter__(self):
        self.quotation_client = QuotationClient(True, True, True, True)
        self.ex_quotation_client = exQuotationClient(True, True, True, True)
        self.quotation_client_connected = False
        self.ex_quotation_client_connected = False

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.quotation_client_connected:
            self.quotation_client.disconnect()
        if self.ex_quotation_client_connected:
            self.ex_quotation_client.disconnect()

    def q_client(self):
        if not self.quotation_client_connected:
            self.quotation_client_connected = self.quotation_client.connect().login()
        return self.quotation_client
    def eq_client(self):
        if not self.ex_quotation_client_connected:
            self.ex_quotation_client_connected = self.ex_quotation_client.connect().login()
        return self.ex_quotation_client
    
    def stock_count(self, market: MARKET):
        '''
        获取股票数量
        Args:
            market: MARKET
        Return: 
            int(count)
        '''
        return self.q_client().get_count(market)
    
    def stock_list(self, market: MARKET, start = 0, count = 0):
        '''
        获取股票列表
        Args:
            market: MARKET
            start?: 起始位置
            count?: 获取数量
        Return: 
            [{
                'code': str(code),
                'name': str(name),
                'pre_close': int(pre_close)
            }, ...]
        '''
        return self.q_client().get_list(market, start, count)
    
    def index_momentum(self, market: MARKET, code: str):
        '''
        获取指数动量
        Args:
            market: MARKET
            code: str(code)
        Return: 
            [momentum...]
        '''
        return self.q_client().get_index_momentum(market, code)
    
    def index_info(self, code_list: MARKET | list[tuple[MARKET, str]], code: str = None):
        '''
        获取指数概况
        支持三种形式的参数
        get_index_info(market, code )
        get_index_info((market, code))
        get_index_info([(market1, code1), (market2, code2)] )
        Args:
            [(market: MARKET(market), code: str(code)), ...]
        Return: 
            [{
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
        return self.q_client().get_index_info(code_list, code)
    
    def stock_kline(self, market: MARKET, code: str, period: PERIOD, start = 0, count = 800, times: int = 1):
        '''
        获取K线数据
        Args:
            market: MARKET
            code: str(code)
            period: PERIOD
            start?: int(start)
            count?: int(count)
            times?: int(times) # 多周期倍数
        Return: 
            [{
                'date_time': str(date_time),
                'open': float(open),
                'high': float(high),
                'low': float(low),
                'close': float(close),
                'vol': int(vol),
                'amount': int(amount),
                'upCount?': int(upcount),
                'downCount?': int(downcount),
            }, ...]
        '''
        return self.q_client().get_kline(market, code, period, start, count, times)
    
    def tick_chart(self, market: MARKET, code: str, start: int = 0, count: int = 0xba00):
        '''
        获取分时图
        Args:
            market: MARKET
            code: str(code)
            start?: int(start)
            count?: int(count)
        Return: 
            [{
                'price': float(price),
                'avg': float(avg),
                'vol': int(vol)
            }, ...]
        '''
        return self.q_client().get_tick_chart(market, code, start, count)

    def stock_quotes_detail(self, code_list: MARKET | list[tuple[MARKET, str]], code: str = None):
        '''
        获取股票详细报价
        支持三种形式的参数
        get_stock_quotes_detail(market, code )
        get_stock_quotes_detail((market, code))
        get_stock_quotes_detail([(market1, code1), (market2, code2)] )
        Args:
            [(market: MARKET(market), code: str(market)), ...]
        Return: 
            [{
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
        '''
        return self.q_client().get_stock_quotes_details(code_list, code)
    
    def stock_top_board(self, category: CATEGORY = CATEGORY.A):
        '''
        获取股票排行榜
        Args:
            category: CATEGORY
        Return: 
            {
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
        return self.q_client().get_stock_top_board(category)
    
    def stock_quotes_list(self, category: CATEGORY, start:int = 0, count: int = 0):
        '''
        获取分类股票报价
        Args:
            category: CATEGORY
            start?: 起始位置
            count?: 获取数量
        Return: 
            [{
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
        return self.q_client().get_stock_quotes_list(category, start, count)
    
    def stock_quotes(self, code_list: MARKET | list[tuple[MARKET, str]], code: str = None):
        '''
        获取股票报价
        支持三种形式的参数
        get_stock_quotes(market, code )
        get_stock_quotes((market, code))
        get_stock_quotes([(market1, code1), (market2, code2)] )
        Args:
            [(market: MARKET(market), code: str(code)), ...]
        Return: 
            [{
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
        return self.q_client().get_quotes(code_list, code)
    
    def stock_unusual(self, market: MARKET, start: int = 0, count: int = 0):
        '''
        获取异动数据
        Args:
            market: MARKET
            start?: int(start)
            count?: int(count)
        Return: 
            [{
                'index': int(index),
                'market': MARKET,
                'code': str(code),
                'time': str(time),
                'desc': str(desc),
                'value': str(value),
            }, ...]
        '''
        return self.q_client().get_unusual(market, start, count)
    
    def stock_history_orders(self, market: MARKET, code: str, date: date):
        '''
        获取历史委托数据
        Args:
            market: MARKET
            code: str(code)
            date: date(date)
        Return: 
            {
                'pre_close': float(pre_close),
                'orders': [{
                    'price': float(price),
                    'vol': int(vol),
                }, ...]
            }
        '''
        return self.q_client().get_history_orders(market, code, date)
    
    def stock_history_transaction(self, market: MARKET, code: str, date: date):
        '''
        获取历史成交数据
        Args:
            market: MARKET
            code: str(code)
            date: date(date)
        Return: 
            {
                'time': str(time),
                'price': float(price),
                'vol': int(vol),
                'trans': int(trans),
                'action': str('SELL'|'BUY'|'NEUTRAL'),
            }
        '''
        return self.q_client().get_history_transaction_with_trans(market, code, date)
    
    def stock_transaction(self, market: MARKET, code: str):
        '''
        获取实时成交数据
        Args:
            market: MARKET
            code: str(code)
        Return: 
            {
                'time': str(time),
                'price': float(price),
                'vol': int(vol),
                'trans': int(trans),
                'action': str('SELL'|'BUY'|'NEUTRAL'),
            }
        '''
        return self.q_client().get_transaction(market, code)

    def stock_history_tick_chart(self, market: MARKET, code: str, date: date):
        '''
        获取历史分时线数据
        Args:
            market: MARKET
            code: str(code)
            date: date(date)
        Return: 
            [{
                'price': float(price),
                'avg': float(avg),
                'vol': int(vol),
            }, ...]
        '''
        return self.q_client().get_history_tick_chart(market, code, date)
    
    def stock_chart_sampling(self, market: MARKET, code: str):
        '''
        获取股票分时缩略
        Args:
            market: MARKET
            code: str(code)
        Return: 
            [float(price), ...]
        '''
        return self.q_client().get_chart_sampling(market, code)
    
    def stock_f10(self, market: MARKET, code: str):
        '''
        获取F10数据
        Args:
            market: MARKET
            code: str(code)
        Return: 
            {
                'name': str(name),
                'content': str(content),
            }
        '''
        return self.q_client().get_company_info(market, code)
    
    def stock_block(self, block_type: BLOCK_FILE_TYPE):
        '''
        获取板块信息
        Args:
            block_type: BLOCK_FILE_TYPE
        Return: 
            [{
                'block_name': str(block_name),
                'stocks': [str(code), ...],
            }, ...]
        '''
        return self.q_client().get_block_file(block_type)
    

    ##########################EX QUOTATION CLIENT##########################
    def goods_count(self):
        '''
        获取扩展市场商品数量
        Return:
            int(count)
        '''
        return self.eq_client().get_count()
    
    def goods_category_list(self):
        '''
        获取商品分类列表
        Return: 
            [{
                'market': EX_MARKET,
                'name': str(name),
                'code': str(code),
                'abbr': str(abbr)
            }, ...]
        '''
        return self.eq_client().get_category_list()

    def goods_detail(self, start = 0, count = 2000):
        '''
        获取商品详情
        Args:
            start?: 起始位置，默认为0
            count?: 获取数量，默认为2000
        Return: 
            [{
                'market': int(market),
                'category': int(category),
                'code': str(code),
                'name': str(name)
            }, ...]
        '''
        return self.eq_client().get_Detail(start, count)
    
    def goods_quotes(self, category: EX_CATEGORY, code: str):
        '''
        获取商品行情
        Args:
            category: EX_CATEGORY(category)
            code: str(code)
        Return: 
            {
                'category': EX_CATEGORY(category),
                'code': str(code),
                'active': int(active),
                'pre_close': float(pre_close),
                'open': float(open),
                'high': float(high),
                'low': float(low),
                'current': float(current),
                'open_position': int(open_position),
                'add_position': int(add_position),
                'vol': int(vol),
                'curr_vol': int(curr_vol),
                'amount': float(amount),
                'in_vol': int(in_vol),
                'ex_vol': int(ex_vol),
                'hold_position': int(hold_position),
                'pending': {
                    'bids': [{'price': float(price), 'vol': int(vol)}, ...],
                    'asks': [{'price': float(price), 'vol': int(vol)}, ...],
                },
                'settlement_price': float(settlement_price),
                'average_price': float(average_price),
                'pre_settlement_price': float(pre_settlement_price),
                'pre_close_price': float(pre_close_price),
                'pre_vol': int(pre_vol),
                'day3_raise': float(day3_raise_percent),
                'settlement_price2': float(settlement_price2),
                'date': date(date),
                'raise_speed': float(raise_speed_percent),
            }
        '''
        return self.eq_client().get_quotes(category, code)
    
    def goods_quotes_list(self, code_list: EX_CATEGORY | list[tuple[EX_CATEGORY, str]], code = None):
        '''
        获取多个商品行情
        支持三种形式的参数
        goods_quotes_list(market, code )
        goods_quotes_list((market, code))
        goods_quotes_list([(market1, code1), (market2, code2)] )
        Args:
            [(category: EX_CATEGORY(category), code: str(code)), ...]
        Return: 
            [{
                'category': EX_CATEGORY(category),
                'code': str(code),
                'active': int(active),
                'pre_close': float(pre_close),
                'open': float(open),
                'high': float(high),
                'low': float(low),
                'current': float(current),
                'open_position': int(open_position),
                'add_position': int(add_position),
                'vol': int(vol),
                'curr_vol': int(curr_vol),
                'amount': float(amount),
                'in_vol': int(in_vol),
                'ex_vol': int(ex_vol),
                'hold_position': int(hold_position),
                'pending': {
                    'bids': [{'price': float(price), 'vol': int(vol)}, ...],
                    'asks': [{'price': float(price), 'vol': int(vol)}, ...],
                },
                'settlement_price': float(settlement_price),
                'average_price': float(average_price),
                'pre_settlement_price': float(pre_settlement_price),
                'pre_close_price': float(pre_close_price),
                'pre_vol': int(pre_vol),
                'day3_raise': float(day3_raise_percent),
                'settlement_price2': float(settlement_price2),
                'date': date(date),
                'raise_speed': float(raise_speed_percent),
            }, ...]
        '''
        return self.eq_client().get_quotes_list(code_list, code)
    
    def goods_kline(self, category: EX_CATEGORY, code: str, period: PERIOD, start: int = 0, count: int = 800, times: int = 1) -> str:
        '''
        获取商品K线图
        Args:
            category: EX_CATEGORY(category)
            code: str(code)
            period: PERIOD(period)
            start?: int(start)
            count?: int(count)
            times?: int(times)
        Return: 
            [{
                'time': datetime(time),
                'open': float(open),
                'hight': float(hight),
                'low': float(low),
                'close': float(close),
                'amount': float(amount),
                'vol': int(vol),
            }, ...]
        '''
        return self.eq_client().get_kline(category, code, period, start, count, times)
    
    def goods_history_transaction(self, category: EX_CATEGORY, code: str, date: date):
        '''
        获取商品历史成交
        Args:
            category: EX_CATEGORY(category)
            date: date(date)
        Return: 
            [{
                'time': time(time),
                'price': float(open),
                'vol': float(hight),
                'action': str('SELL'|'BUY'|'NEUTRAL')
            }, ...]
        '''
        return self.eq_client().get_history_transaction(category, code, date)
    
    def goods_table(self):
        '''
        获取商品名称表
        Return: 
            str(type#code|name, ...)
        '''
        return self.eq_client().get_table()
    
    def goods_table_detail(self):
        '''
        获取商品名称表详情
        Return: 
            str(type#code|...|...|..., ...)
        '''
        return self.eq_client().get_table_detail()
    
    def futures_quotes_list(self, category: EX_CATEGORY):
        '''
        获取期货商品行情列表
        Args:
            category: EX_CATEGORY(category)
        Return: 
            [{
                'category': EX_CATEGORY(category),
                'code': str(code),
                'active': int(active),
                'pre_close': float(pre_close),
                'open': float(open),
                'high': float(high),
                'low': float(low),
                'current': float(current),
                'open_position': int(open_position),
                'add_position': int(add_position),
                'vol': int(vol),
                'curr_vol': int(curr_vol),
                'amount': float(amount),
                'in_vol': int(in_vol),
                'ex_vol': int(ex_vol),
                'hold_position': int(hold_position),
                'pending': {
                    'bids': [{'price': float(price), 'vol': int(vol)}, ...],
                    'asks': [{'price': float(price), 'vol': int(vol)}, ...],
                },
                'settlement_price': float(settlement_price),
                'average_price': float(average_price),
                'pre_settlement_price': float(pre_settlement_price),
                'pre_close_price': float(pre_close_price),
                'pre_vol': int(pre_vol),
                'day3_raise': float(day3_raise_percent),
                'settlement_price2': float(settlement_price2),
                'date': date(date),
                'raise_speed': float(raise_speed_percent),
            }, ...]
        '''
        return self.eq_client().get_futures_quotes_list(category)
    
    def futures_quotes(self, code_list: EX_CATEGORY | list[tuple[EX_CATEGORY, str]], code = None):
        '''
        获取多个期货商品行情
        支持三种形式的参数
        futures_quotes(market, code )
        futures_quotes((market, code))
        futures_quotes([(market1, code1), (market2, code2)] )
        Args:
            [(category: EX_CATEGORY(category), code: str(code)), ...] # 期货商品列表
        Return: 
            [{
                'category': EX_CATEGORY(category),
                'code': str(code),
                'active': int(active),
                'pre_close': float(pre_close),
                'open': float(open),
                'high': float(high),
                'low': float(low),
                'current': float(current),
                'open_position': int(open_position),
                'add_position': int(add_position),
                'vol': int(vol),
                'curr_vol': int(curr_vol),
                'amount': float(amount),
                'in_vol': int(in_vol),
                'ex_vol': int(ex_vol),
                'hold_position': int(hold_position),
                'pending': {
                    'bids': [{'price': float(price), 'vol': int(vol)}, ...],
                    'asks': [{'price': float(price), 'vol': int(vol)}, ...],
                },
                'settlement_price': float(settlement_price),
                'average_price': float(average_price),
                'pre_settlement_price': float(pre_settlement_price),
                'pre_close_price': float(pre_close_price),
                'pre_vol': int(pre_vol),
                'day3_raise': float(day3_raise_percent),
                'settlement_price2': float(settlement_price2),
                'date': date(date),
                'raise_speed': float(raise_speed_percent),
            }, ...]
        '''
        return self.eq_client().get_futures_quotes(code_list)
    
    def goods_tick_chart(self, category: EX_CATEGORY, code: str):
        '''
        获取商品分时图
        Args:
            category: EX_CATEGORY,
            code: str(code)
        Return: 
            [{
                'time': time(time),
                'price': float(price),
                'avg': float(avg),
                'vol': int(vol)
            }, ...]
        '''
        return self.eq_client().get_tick_chart(category, code)
    
    def goods_history_tick_chart(self, category: EX_CATEGORY, code: str, date: date):
        '''
        获取商品历史分时图
        Args:
            category: EX_CATEGORY
            code: str(code)
            date: date(date)
        Return: 
            [{
                'time': time(time),
                'price': float(price),
                'avg': float(avg),
                'vol': int(vol)
            }, ...]
        '''
        return self.eq_client().get_history_tick_chart(category, code, date)
    
    def goods_chart_sampling(self, category: EX_CATEGORY, code: str):
        '''
        获取商品分时图缩略
        Args:
            category: EX_CATEGORY,
            code: str(code)
        Return: 
            [float(price), ...]
        '''
        return self.eq_client().get_chart_sampling(category, code)
    


if __name__ == '__main__':
    
    with TdxClient() as client:

        print(client.stock_count(MARKET.SZ))
        # print(pd.DataFrame(client.stock_list(MARKET.SZ)))
        # print(pd.DataFrame(client.index_momentum(MARKET.SZ, '399001')))
        # print(pd.DataFrame(client.index_momentum(MARKET.SH, '999999')))
        # print(pd.DataFrame(client.index_info([(MARKET.SZ, '399001'), (MARKET.SH, '999999')])))
        # print(pd.DataFrame(client.stock_kline(MARKET.SH, '999999', PERIOD.DAILY)))
        # print(pd.DataFrame(client.stock_kline(MARKET.SH, '999999', PERIOD.MINS, times=10)))
        # print(pd.DataFrame(client.tick_chart(MARKET.SH, '999999')))
        # print(pd.DataFrame(client.tick_chart(MARKET.SZ, '000001')))
        # print(pd.DataFrame(client.stock_quotes_detail(MARKET.SZ, '000001')))
        # print(pd.DataFrame(client.stock_top_board()))
        # print(pd.DataFrame(client.stock_quotes_list(CATEGORY.A)))
        # print(pd.DataFrame(client.stock_quotes(MARKET.SZ, '000001')))
        # print(pd.DataFrame(client.stock_unusual(MARKET.SZ)))
        # print(pd.DataFrame(client.stock_history_orders(MARKET.SZ, '000001', date(2026, 3, 16))))
        # print(pd.DataFrame(client.stock_history_transaction(MARKET.SZ, '000001', date(2026, 3, 16))))
        # print(pd.DataFrame(client.stock_transaction(MARKET.SZ, '000001')))
        # print(pd.DataFrame(client.stock_history_tick_chart(MARKET.SZ, '000001', date(2026, 3, 16))))
        # print(pd.DataFrame(client.stock_chart_sampling(MARKET.SZ, '000001')))
        # print(pd.DataFrame(client.stock_f10(MARKET.SZ, '000001')))

        # print(client.goods_count())
        # print(pd.DataFrame(client.goods_category_list()))
        # print(pd.DataFrame(client.goods_detail()))
        # print(pd.DataFrame([client.goods_quotes(EX_CATEGORY.US_STOCK, 'TSLA')]))
        # print(pd.DataFrame(client.goods_quotes_list([(EX_CATEGORY.US_STOCK, 'TSLA')])))
        # print(pd.DataFrame(client.goods_kline(EX_CATEGORY.US_STOCK, 'TSLA', PERIOD.DAILY)))
        # print(pd.DataFrame(client.goods_history_transaction(EX_CATEGORY.US_STOCK, 'TSLA', date(2026, 3, 3))))
        # print(client.goods_table())
        # print(client.goods_table_detail())
        # print(pd.DataFrame(client.futures_quotes_list(EX_CATEGORY.US_STOCK)))
        # print(pd.DataFrame(client.futures_quotes([(EX_CATEGORY.US_STOCK, 'TSLA')])))
        # print(pd.DataFrame(client.goods_tick_chart(EX_CATEGORY.US_STOCK, 'TSLA')))
        # print(pd.DataFrame(client.goods_history_tick_chart(EX_CATEGORY.US_STOCK, 'TSLA', date(2026, 3, 3))))
        # print(pd.DataFrame(client.goods_chart_sampling(EX_CATEGORY.US_STOCK, 'TSLA')))