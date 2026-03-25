

from datetime import date
import pandas as pd

from client.exQuotationClient import exQuotationClient
from client.quotationClient import QuotationClient
from const import BLOCK_FILE_TYPE, CATEGORY, EX_CATEGORY, FILTER_TYPE, MARKET, PERIOD, SORT_TYPE

class TdxClient:
    def __enter__(self):
        self.quotation_client = QuotationClient(True, True)
        self.ex_quotation_client = exQuotationClient(True, True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.quotation_client.connected:
            self.quotation_client.disconnect()
        if self.ex_quotation_client.connected:
            self.ex_quotation_client.disconnect()

    def q_client(self):
        if not self.quotation_client.connected:
            self.quotation_client.connect().login()
        return self.quotation_client
    
    def eq_client(self):
        if not self.ex_quotation_client.connected:
            self.ex_quotation_client.connect().login()
        return self.ex_quotation_client
    
    def stock_count(self, market: MARKET) -> int:
        '''
        获取股票数量
        Args:
             market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
        Return: 
            count: int      - 股票数量
        '''
        return self.q_client().get_count(market)
    
    def stock_list(self, market: MARKET, start = 0, count = 0) -> list[dict]:
        '''
        获取股票列表
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            start: int     - 起始位置，默认为0
            count: int     - 获取数量，默认为0（获取全部）
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - code: str      - 股票代码
                - name: str      - 股票名称
                - pre_close: int - 昨日收盘价
        '''
        return self.q_client().get_list(market, start, count)
    
    def stock_vol_profile(self, market: MARKET, code: str) -> list[dict]:
        '''
        获取指数动量
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            code: str      - 指数代码
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str           - 指数代码
                - open: float         - 今开
                - high: float         - 最高
                - low: float          - 最低
                - close: float        - 现价
                - pre_close: float    - 昨收
                - diff: float         - 涨跌
                - cur_vol: int        - 现量
                - vol: int            - 总量
                - amount: int         - 总金额
                - in_vol: int         - 内盘
                - out_vol: int        - 外盘
                - s_amount: int       - 上涨数
                - open_amount: int    - 开盘金额
                - active: int         - 活跃度
                - handicap: Dict      - 3档盘口
                    - bid: list[dict] - 买盘
                        - price: float- 价格
                        - vol: int    - 买量
                    - ask: list[dict] - 卖盘
                        - price: float- 价格
                        - vol: int    - 卖量
                - vol_profile: list[dict] - 成交分布
                    - price: float    - 价格
                    - vol: int        - 成交量
                    - buy: int        - 主买量
                    - sell: int       - 主卖量

        '''
        return self.q_client().get_vol_profile(market, code) 
    
    def index_momentum(self, market: MARKET, code: str) -> list[int]:
        '''
        获取指数动量
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            code: str      - 指数代码
        Return: 
            List[int]: 动量列表
        '''
        return self.q_client().get_index_momentum(market, code)
    
    def index_info(self, code_list: MARKET | list[tuple[MARKET, str]], code: str = None) -> list[int]:
        '''
        获取指数概况
        支持三种形式的参数
        get_index_info(market, code )
        get_index_info((market, code))
        get_index_info([(market1, code1), (market2, code2)] )
        Args:
            List[tuple]: 股票列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str           - 指数代码
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str           - 指数代码
                - open: float         - 开盘价
                - high: float         - 最高价
                - low: float          - 最低价
                - close: float        - 收盘价
                - pre_close: float    - 昨日收盘价
                - diff: float         - 涨跌
                - vol: int            - 成交量
                - amount: int         - 成交额
                - up_count: int       - 上涨数
                - down_count: int     - 下跌数
                - active: int         - 活跃度
        '''
        return self.q_client().get_index_info(code_list, code)
    
    def stock_kline(self, market: MARKET, code: str, period: PERIOD, start = 0, count = 800, times: int = 1) -> list[dict]:
        '''
        获取K线数据
        Args:
            market: MARKET  - 市场类型
            code: str       - 股票代码
            period: PERIOD  - K线周期
            start: int      - 起始位置，默认为0
            count: int      - 获取数量，默认为800
            times: int      - 多周期倍数，默认为1
        Returns:
            List[Dict]: K线数据列表，每个元素包含：
                - date_time: datetime   - 时间
                - open: float           - 开盘价
                - high: float           - 最高价
                - low: float            - 最低价
                - close: float          - 收盘价
                - vol: int              - 成交量
                - amount: int           - 成交额
                - upCount?: int         - 上涨数（指数专有）
                - downCount?: int       - 下跌数（指数专有）
        '''
        return self.q_client().get_kline(market, code, period, start, count, times)
    
    def stock_tick_chart(self, market: MARKET, code: str, date: date = None, start: int = 0, count: int = 0xba00) -> list[dict]:
        '''
        获取分时图
        Args:
            market: MARKET - 市场类型
            code: str  - 股票代码
            date: date - 日期，默认为None（查询当日分时图）
            start: int - 起始位置，默认为0
            count: int - 获取数量，默认为800
        Returns:
            List[Dict]: 分时数据列表，每个元素包含：
                - price: float - 成交价
                - avg: float   - 平均价
                - vol: int     - 成交量
        '''
        return self.q_client().get_tick_chart(market, code, date, start, count)

    def stock_quotes_detail(self, code_list: MARKET | list[tuple[MARKET, str]], code: str = None) -> list[dict]:
        '''
        获取股票详细报价
        支持三种形式的参数
        get_stock_quotes_detail(market, code )
        get_stock_quotes_detail((market, code))
        get_stock_quotes_detail([(market1, code1), (market2, code2)] )
        Args:
            List[tuple]: 股票列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str           - 股票代码
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str           - 股票代码
                - name: str           - 股票名称
                - open: float         - 今开
                - high: float         - 最高
                - low: float          - 最低
                - close: float        - 现价
                - pre_close: float    - 昨收
                - server_time: str    - 服务器时间
                - neg_price: float    - 价格负数
                - vol: int            - 总量
                - cur_vol: int        - 现量
                - amount: int         - 总金额
                - in_vol: int         - 内盘
                - out_vol: int        - 外盘
                - s_amount: int       - 上涨数
                - open_amount: int    - 开盘金额
                - handicap: Dict      - 5档盘口
                    - bid: list[dict] - 买盘
                        - price: float- 买价
                        - vol: int    - 买量
                    - ask: list[dict] - 卖盘
                        - price: float- 卖价
                        - vol: int    - 卖量
                - rise_speed: int     - 涨速
                - short_turnover: int - 短换手
                - min2_amount: int    - 2分钟金额
                - opening_rush: int   - 开盘抢筹
                - vol_rise_speed: int - 量涨速
                - depth: int          - 委比
                - active: int         - 活跃度
        '''
        return self.q_client().get_stock_quotes_details(code_list, code)
    
    def stock_top_board(self, category: CATEGORY = CATEGORY.A) -> dict:
        '''
        获取股票排行榜
        Args:
            - category: CATEGORY  市场分类（SH: 上证A, SZ: 深证A, A: A股, B: B股, KCB: 科创板, BJ: 北证A, CYB: 创业板）
        Return: 
            Dict: 
                - increase: list[dict]  - 涨幅榜
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 涨幅
                - decrease: list[dict]  - 跌幅榜
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 跌幅
                - amplitude: list[dict]  - 振幅榜
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 振幅
                - rise_speed: list[dict]  - 涨速榜
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 涨速
                - fall_speed: list[dict]  - 跌速榜
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 跌速
                - vol_ratio: list[dict]  - 量比榜
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 量比
                - pos_commission_ratio: list[dict]  - 委比正序
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 委比
                - neg_commission_ratio: list[dict]  - 委比倒序
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 委比
                - turnover: list[dict]  - 换手率榜
                    - market: MARKET    - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                    - code: str         - 指数代码
                    - price: float      - 现价
                    - value: float      - 换手率
        '''
        return self.q_client().get_stock_top_board(category)
    
    def stock_quotes_list(self, category: CATEGORY, start:int = 0, count: int = 80, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False, filter: list[FILTER_TYPE] = []) -> list[dict]:
        '''
        获取各类股票行情列表
        Args:
            category: CATEGORY        - 市场分类（SH: 上证A, SZ: 深证A, A: A股, B: B股, KCB: 科创板, BJ: 北证A, CYB: 创业板）
            start: int                - 起始位置
            count: int                - 获取数量
            sortType: SORT_TYPE       - 排序类型
            reverse: bool             - 倒序排序
            filter: list[FILTER_TYPE] - 过滤类型
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str           - 股票代码
                - name: str           - 股票名称
                - open: float         - 今开
                - high: float         - 最高
                - low: float          - 最低
                - close: float        - 现价
                - pre_close: float    - 昨收
                - server_time: str    - 服务器时间
                - neg_price: float    - 价格负数
                - vol: int            - 总量
                - cur_vol: int        - 现量
                - amount: int         - 总金额
                - in_vol: int         - 内盘
                - out_vol: int        - 外盘
                - s_amount: int       - 上涨数
                - open_amount: int    - 开盘金额
                - handicap: Dict      - 1档盘口
                    - bid: list[dict] - 买盘
                        - price: float- 买价
                        - vol: int    - 买量
                    - ask: list[dict] - 卖盘
                        - price: float- 卖价
                        - vol: int    - 卖量
                - rise_speed: int     - 涨速
                - short_turnover: int - 短换手
                - min2_amount: int    - 2分钟金额
                - opening_rush: int   - 开盘抢筹
                - vol_rise_speed: int - 量涨速
                - depth: int          - 委比
                - active: int         - 活跃度
        '''
        return self.q_client().get_stock_quotes_list(category, start, count, sortType, reverse, filter)
    
    def stock_quotes(self, code_list: MARKET | list[tuple[MARKET, str]], code: str = None) -> list[dict]:
        '''
        获取股票报价
        支持三种形式的参数
        get_stock_quotes(market, code )
        get_stock_quotes((market, code))
        get_stock_quotes([(market1, code1), (market2, code2)] )
        Args:
            List[tuple]: 股票列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str           - 股票代码
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str           - 股票代码
                - name: str           - 股票名称
                - open: float         - 今开
                - high: float         - 最高
                - low: float          - 最低
                - close: float        - 现价
                - pre_close: float    - 昨收
                - server_time: str    - 服务器时间
                - neg_price: float    - 价格负数
                - vol: int            - 总量
                - cur_vol: int        - 现量
                - amount: int         - 总金额
                - in_vol: int         - 内盘
                - out_vol: int        - 外盘
                - s_amount: int       - 上涨数
                - open_amount: int    - 开盘金额
                - handicap: Dict      - 1档盘口
                    - bid: list[dict] - 买盘
                        - price: float- 买价
                        - vol: int    - 买量
                    - ask: list[dict] - 卖盘
                        - price: float- 卖价
                        - vol: int    - 卖量
                - rise_speed: int     - 涨速
                - short_turnover: int - 短换手
                - min2_amount: int    - 2分钟金额
                - opening_rush: int   - 开盘抢筹
                - vol_rise_speed: int - 量涨速
                - depth: int          - 委比
                - active: int         - 活跃度
        '''
        return self.q_client().get_quotes(code_list, code)
    
    def stock_unusual(self, market: MARKET, start: int = 0, count: int = 0) -> list[dict]:
        '''
        获取异动数据
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            start: int      - 起始位置，默认为0
            count: int      - 获取数量，默认为0（获取全部）
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - index: int     - 序号
                - market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
                - code: str      - 股票代码
                - time: time     - 时间
                - desc: str      - 异动类型
                - value: str     - 异动值
        '''
        return self.q_client().get_unusual(market, start, count)
    
    def stock_auction(self, market: MARKET, code: str) -> list[dict]:
        '''
        获取竞价数据
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            code: str      - 指数代码
        Return: 
            List[Dict]: 股票竞价列表，每个元素包含：
                - time: time        - 时间
                - price: float      - 撮合价
                - matched: int      - 匹配量
                - unmatched: int    - 未匹配量
        '''
        return self.q_client().get_auction(market, code)
    
    def stock_history_orders(self, market: MARKET, code: str, date: date) -> list[dict]:
        '''
        获取历史委托数据
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            code: str      - 指数代码
            date: date     - 日期
        Return: 
            List[Dict]: 股票委托列表，每个元素包含：
                - price: float  - 价格
                - vol: int      - 成交量
        '''
        return self.q_client().get_history_orders(market, code, date)
    
    def stock_transaction(self, market: MARKET, code: str, date: date = None) -> list[dict]:
        '''
        获取历史成交数据
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            code: str      - 指数代码
            date: date     - 日期，默认为None（获取实时成交数据）
        Return: 
            List[Dict]: 股票历史列表，每个元素包含：
                - time: time        - 时间
                - price: float      - 价格
                - vol: int          - 成交量
                - trans: int        - 成交笔数
                - action: str       - 成交方向（SELL，BUY，NEUTRAL）
        '''
        return self.q_client().get_transaction(market, code, date)

    def stock_chart_sampling(self, market: MARKET, code: str) -> list[float]:
        '''
        获取股票分时缩略
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            code: str      - 指数代码
        Return: 
            List[float]:    - 价格
        '''
        return self.q_client().get_chart_sampling(market, code)
    
    def stock_f10(self, market: MARKET, code: str) -> list[dict]:
        '''
        获取F10数据
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            code: str      - 指数代码
        Return: 
            List[Dict]:  股票公司信息
                - name: str
                - content: str | dict
        '''
        return self.q_client().get_company_info(market, code)
    
    def stock_block(self, block_type: BLOCK_FILE_TYPE) -> list[dict]:
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
    def goods_count(self) -> int:
        '''
        获取扩展市场商品数量
        Return: 
            count: int      - 股票数量
        '''
        return self.eq_client().get_count()
    
    def goods_category_list(self) -> list[dict]:
        '''
        获取商品分类列表
        Return: 
            List[Dict]: 商品类别列表，每个元素包含：
                - market: EX_MARKET - 扩展市场
                - code: str         - 商品代码
                - name: str         - 商品名称
                - abbr: str         - 缩写
        '''
        return self.eq_client().get_category_list()

    def goods_list(self, start = 0, count = 2000) -> list[dict]:
        '''
        获取商品列表
        Args:
            start: int      - 起始位置，默认为0
            count: int      - 获取数量，默认为2000
        Return: 
            List[Dict]: 商品列表，每个元素包含：
                - market: int       - 扩展市场
                - category: int     - 扩展市场类别
                - code: str         - 商品代码
                - name: str         - 商品名称
        '''
        return self.eq_client().get_list(start, count)
    
    def goods_quotes_list(self, category: EX_CATEGORY, start: int = 0, count: int = 100, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False) -> list[dict]:
        '''
        获取期货商品行情列表
        Args:
            category: EX_CATEGORY     - 扩展市场类别
            start: int                - 起始位置
            count: int                - 获取数量
            sortType: SORT_TYPE       - 排序类型
            reverse: bool             - 倒序排序
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - category: EX_CATEGORY - 扩展市场类别
                - code: str             - 股票代码
                - open: float           - 今开
                - high: float           - 最高
                - low: float            - 最低
                - close: float          - 现价
                - open_position: int    - 开仓量
                - add_position: int     - 平仓量
                - hold_position: int    - 持仓量
                - vol: int              - 总量
                - curr_vol: int         - 现量
                - amount: int           - 总金额
                - in_vol: int           - 内盘
                - out_vol: int          - 外盘
                - handicap: Dict        - 5档盘口
                    - bid: list[dict]   - 买盘
                        - price: float  - 买价
                        - vol: int      - 买量
                    - ask: list[dict]   - 卖盘
                        - price: float  - 卖价
                        - vol: int      - 卖量

                - settlement: float     - 结算价
                - avg: float            - 均价
                - pre_settlement: float - 昨结算价
                - pre_close: float      - 昨收
                - pre_vol: int          - 昨总量
                - day3_raise: float     - 3日涨幅
                - settlement2: float    - 结算价
                - date: date            - 日期
                - raise_speed: float    - 涨速
                - active: int           - 活跃度
        '''
        return self.eq_client().get_quotes_list(category, start, count, sortType, reverse)
    
    def goods_quotes(self, code_list: EX_CATEGORY | list[tuple[EX_CATEGORY, str]], code = None) -> list[dict]:
        '''
        获取多个期货商品行情
        支持三种形式的参数
        goods_quotes(market, code )
        goods_quotes((market, code))
        goods_quotes([(market1, code1), (market2, code2)] )
        Args:
            List[tuple]: 商品列表，每个元素包含：
                - category: EX_CATEGORY - 扩展市场类别
                - code: str             - 商品代码
        Return: 
            List[Dict]: 股票信息列表，每个元素包含：
                - category: EX_CATEGORY - 扩展市场类别
                - code: str             - 股票代码
                - open: float           - 今开
                - high: float           - 最高
                - low: float            - 最低
                - close: float          - 现价
                - open_position: int    - 开仓量
                - add_position: int     - 平仓量
                - hold_position: int    - 持仓量
                - vol: int              - 总量
                - curr_vol: int         - 现量
                - amount: int           - 总金额
                - in_vol: int           - 内盘
                - out_vol: int          - 外盘
                - handicap: Dict        - 5档盘口
                    - bid: list[dict]   - 买盘
                        - price: float  - 买价
                        - vol: int      - 买量
                    - ask: list[dict]   - 卖盘
                        - price: float  - 卖价
                        - vol: int      - 卖量

                - settlement: float     - 结算价
                - avg: float            - 均价
                - pre_settlement: float - 昨结算价
                - pre_close: float      - 昨收
                - pre_vol: int          - 昨总量
                - day3_raise: float     - 3日涨幅
                - settlement2: float    - 结算价
                - date: date            - 日期
                - raise_speed: float    - 涨速
                - active: int           - 活跃度
        '''
        return self.eq_client().get_quotes(code_list, code)
    
    def goods_kline(self, category: EX_CATEGORY, code: str, period: PERIOD, start: int = 0, count: int = 800, times: int = 1) -> list[dict]:
        '''
        获取商品K线图
        Args:
            category: EX_CATEGORY   - 扩展市场类别
            code: str                   - 商品代码
            period: PERIOD          - K线周期
            start: int              - 起始位置，默认为0
            count: int              - 获取数量，默认为800
            times: int              - 多周期倍数，默认为1
        Returns:
            List[Dict]: K线数据列表，每个元素包含：
                - date_time: datetime   - 时间
                - open: float           - 开盘价
                - high: float           - 最高价
                - low: float            - 最低价
                - close: float          - 收盘价
                - vol: int              - 成交量
                - amount: float         - 成交额
        '''
        return self.eq_client().get_kline(category, code, period, start, count, times)
    
    def goods_history_transaction(self, category: EX_CATEGORY, code: str, date: date) -> list[dict]:
        '''
        获取商品历史成交
        Args:
            category: EX_CATEGORY   - 扩展市场类别
            date: date - 日期，默认为None（查询当日分时图）
        Return: 
            List[Dict]: 股票历史列表，每个元素包含：
                - time: time        - 时间
                - price: float      - 价格
                - vol: int          - 成交量
                - action: str       - 成交方向（SELL，BUY，NEUTRAL）
        '''
        return self.eq_client().get_history_transaction(category, code, date)

    def goods_tick_chart(self, category: EX_CATEGORY, code: str, date: date = None) -> list[dict]:
        '''
        获取商品分时图
        Args:
            category: EX_CATEGORY - 市场类型
            code: str  - 商品代码
            date: date - 日期，默认为None（查询当日分时图）
        Return: 
            List[Dict]: 商品分时列表，每个元素包含：
                - time: time        - 时间
                - price: float      - 价格
                - avg: float        - 均价
                - vol: int          - 成交量
        '''
        return self.eq_client().get_tick_chart(category, code, date)
    
    def goods_chart_sampling(self, category: EX_CATEGORY, code: str) -> list[float]:
        '''
        获取商品分时图缩略
        Args:
            category: EX_CATEGORY   - 市场类型
            code: str               - 商品代码
        Return: 
            List[float]             - 价格列表
        '''
        return self.eq_client().get_chart_sampling(category, code)
    


if __name__ == '__main__':
    
    with TdxClient() as client:

        print(client.stock_count(MARKET.SZ))
        print(pd.DataFrame(client.stock_list(MARKET.SZ)))
        print(pd.DataFrame(client.index_momentum(MARKET.SZ, '399001')))
        print(pd.DataFrame(client.index_momentum(MARKET.SH, '999999')))
        print(pd.DataFrame(client.index_info([(MARKET.SZ, '399001'), (MARKET.SH, '999999')])))
        print(pd.DataFrame(client.stock_kline(MARKET.SH, '999999', PERIOD.DAILY)))
        print(pd.DataFrame(client.stock_kline(MARKET.SH, '999999', PERIOD.MINS, times=10)))
        print(pd.DataFrame(client.stock_tick_chart(MARKET.SH, '999999')))
        print(pd.DataFrame(client.stock_tick_chart(MARKET.SZ, '000001')))
        print(pd.DataFrame(client.stock_tick_chart(MARKET.SZ, '000001', date(2026, 3, 16))))
        print(pd.DataFrame(client.stock_quotes_detail(MARKET.SZ, '000001')))
        print(pd.DataFrame(client.stock_top_board()))
        print(pd.DataFrame(client.stock_quotes_list(CATEGORY.A, count = 0, sortType=SORT_TYPE.TOTAL_AMOUNT)))
        print(pd.DataFrame(client.stock_quotes(MARKET.SZ, '000001')))
        print(pd.DataFrame(client.stock_unusual(MARKET.SZ)))
        print(pd.DataFrame(client.stock_auction(MARKET.SZ, '300308')))
        print(pd.DataFrame(client.stock_history_orders(MARKET.SZ, '000001', date(2026, 3, 16))))
        print(pd.DataFrame(client.stock_transaction(MARKET.SZ, '000001')))
        print(pd.DataFrame(client.stock_transaction(MARKET.SZ, '000001', date(2026, 3, 16))))
        print(pd.DataFrame(client.stock_chart_sampling(MARKET.SZ, '000001')))
        print(pd.DataFrame(client.stock_f10(MARKET.SZ, '000001')))

        print(client.goods_count())
        print(pd.DataFrame(client.goods_category_list()))
        print(pd.DataFrame(client.goods_list()))
        print(pd.DataFrame(client.goods_quotes_list(EX_CATEGORY.US_STOCK, sortType=SORT_TYPE.TOTAL_AMOUNT)))
        print(pd.DataFrame([client.goods_quotes(EX_CATEGORY.US_STOCK, 'TSLA')]))
        print(pd.DataFrame(client.goods_quotes([(EX_CATEGORY.US_STOCK, 'TSLA'), (EX_CATEGORY.HK_MAIN_BOARD, '09988')])))
        print(pd.DataFrame(client.goods_kline(EX_CATEGORY.US_STOCK, 'TSLA', PERIOD.DAILY)))
        print(pd.DataFrame(client.goods_history_transaction(EX_CATEGORY.US_STOCK, 'TSLA', date(2026, 3, 3))))
        print(pd.DataFrame(client.goods_tick_chart(EX_CATEGORY.US_STOCK, 'TSLA')))
        print(pd.DataFrame(client.goods_tick_chart(EX_CATEGORY.US_STOCK, 'TSLA', date(2026, 3, 3))))
        print(pd.DataFrame(client.goods_chart_sampling(EX_CATEGORY.US_STOCK, 'TSLA')))