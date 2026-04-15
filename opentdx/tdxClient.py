from __future__ import annotations

from datetime import date
from typing import Optional

from opentdx.client.ExQuotationClient import ExQuotationClient
from opentdx.client.MacQuotationClient import MacQuotationClient
from opentdx.client.quotationClient import QuotationClient
from opentdx.const import ADJUST, BLOCK_FILE_TYPE, BOARD_TYPE, CATEGORY, EX_BOARD_TYPE, EX_MARKET, FILTER_TYPE, MARKET, PERIOD, SORT_TYPE, mac_ex_hosts

class TdxClient:
    def __init__(self):
        self.quotation_client = QuotationClient(multithread=True, heartbeat=True)
        self.ex_quotation_client = ExQuotationClient(multithread=True, heartbeat=True)
        self.mac_client = MacQuotationClient(multithread=True, heartbeat=True)
        self.mac_ex_client = MacQuotationClient(multithread=True, heartbeat=True, hosts=mac_ex_hosts)

    def __enter__(self):
        self.quotation_client.connect().login()
        self.ex_quotation_client.connect().login()
        self.mac_client.connect()
        self.mac_ex_client.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for client in [self.quotation_client, self.ex_quotation_client, self.mac_client, self.mac_ex_client]:
            if client.connected:
                client.disconnect()

    # ── 连接管理 ──────────────────────────────────────────

    def _ensure_client(self, attr: str, needs_login=False):
        client = getattr(self, attr)
        if not client.connected:
            client.connect()
            if needs_login:
                client.login()
        return client

    def q_client(self):
        return self._ensure_client('quotation_client', needs_login=True)

    def eq_client(self):
        return self._ensure_client('ex_quotation_client', needs_login=True)

    def mac_client(self):
        return self._ensure_client('mac_client')

    def mac_ex_client(self):
        return self._ensure_client('mac_ex_client')

    def _mac_for(self, market):
        """根据 market 类型路由到对应的 MAC client"""
        if isinstance(market, (EX_BOARD_TYPE, EX_MARKET)):
            return self.mac_ex_client()
        return self.mac_client()

    # ── A股行情 (QuotationClient) ────────────────────────

    def stock_count(self, market: MARKET) -> int:
        '''
        获取股票数量
        Args:
             market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
        Return:
            count: int      - 股票数量
        '''
        return self.q_client().get_count(market)

    def stock_list(self, market: MARKET, start=0, count=0) -> list[dict]:
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
        获取股票成交分布
        Args:
            market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            code: str      - 股票代码
        Return:
            List[Dict]: 股票信息列表，每个元素包含：
                - market: MARKET      - 市场类型
                - code: str           - 股票代码
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

    def index_info(self, code_list, code=None) -> list[dict]:
        '''
        获取指数概况
        支持三种形式的参数
        index_info(market, code)
        index_info((market, code))
        index_info([(market1, code1), (market2, code2)])
        Args:
            code_list: MARKET | list[tuple[MARKET, str]] - 指数列表
            code: str   - 指数代码（当 code_list 为 MARKET 时使用）
        Return:
            List[Dict]: 指数信息列表，每个元素包含：
                - market: MARKET      - 市场类型
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

    def stock_kline(self, market: MARKET, code: str, period: PERIOD, start=0, count=800, times: int = 1, adjust: ADJUST = ADJUST.NONE) -> list[dict]:
        '''
        获取K线数据
        Args:
            market: MARKET  - 市场类型
            code: str       - 股票代码
            period: PERIOD  - K线周期
            start: int      - 起始位置，默认为0
            count: int      - 获取数量，默认为800
            times: int      - 多周期倍数，默认为1
            adjust: ADJUST  - 复权类型
        Returns:
            List[Dict]: K线数据列表，每个元素包含：
                - datetime: datetime    - 时间
                - open: float           - 开盘价
                - high: float           - 最高价
                - low: float            - 最低价
                - close: float          - 收盘价
                - vol: int              - 成交量
                - amount: int           - 成交额
                - up_count?: int        - 上涨数（指数专有）
                - down_count?: int      - 下跌数（指数专有）
        '''
        return self.q_client().get_kline(market, code, period, start, count, times, adjust)

    def stock_tick_chart(self, market: MARKET, code: str, date: date = None, start: int = 0, count: int = 0xba00) -> list[dict]:
        '''
        获取分时图
        Args:
            market: MARKET - 市场类型
            code: str  - 股票代码
            date: date - 日期，默认为None（查询当日分时图）
            start: int - 起始位置，默认为0
            count: int - 获取数量，默认为0xba00
        Returns:
            List[Dict]: 分时数据列表，每个元素包含：
                - price: float - 成交价
                - avg: float   - 平均价
                - vol: int     - 成交量
        '''
        return self.q_client().get_tick_chart(market, code, date, start, count)

    def stock_quotes_detail(self, code_list, code=None) -> list[dict]:
        '''
        获取股票详细报价（5档盘口）
        支持三种形式的参数
        stock_quotes_detail(market, code)
        stock_quotes_detail((market, code))
        stock_quotes_detail([(market1, code1), (market2, code2)])
        Args:
            code_list: MARKET | list[tuple[MARKET, str]] - 股票列表
            code: str   - 股票代码
        Return:
            List[Dict]: 股票信息列表，每个元素包含：
                - market: MARKET      - 市场类型
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
            category: CATEGORY  市场分类（SH: 上证A, SZ: 深证A, A: A股, B: B股, KCB: 科创板, BJ: 北证A, CYB: 创业板）
        Return:
            Dict:
                - increase: list[dict]  - 涨幅榜
                - decrease: list[dict]  - 跌幅榜
                - amplitude: list[dict]  - 振幅榜
                - rise_speed: list[dict]  - 涨速榜
                - fall_speed: list[dict]  - 跌速榜
                - vol_ratio: list[dict]  - 量比榜
                - pos_commission_ratio: list[dict]  - 委比正序
                - neg_commission_ratio: list[dict]  - 委比倒序
                - turnover: list[dict]  - 换手率榜
            每个榜单元素:
                - market: MARKET  - 市场类型
                - code: str       - 股票代码
                - price: float    - 现价
                - value: float    - 榜单数值
        '''
        return self.q_client().get_stock_top_board(category)

    def stock_quotes_list(self, category: CATEGORY, start: int = 0, count: int = 80, sort_type: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False, filter_types: Optional[list[FILTER_TYPE]] = None) -> list[dict]:
        '''
        获取各类股票行情列表
        Args:
            category: CATEGORY        - 市场分类（SH: 上证A, SZ: 深证A, A: A股, B: B股, KCB: 科创板, BJ: 北证A, CYB: 创业板）
            start: int                - 起始位置
            count: int                - 获取数量
            sort_type: SORT_TYPE       - 排序类型
            reverse: bool             - 倒序排序
            filter_types: list[FILTER_TYPE] - 过滤类型
        Return:
            List[Dict]: 股票信息列表，每个元素包含：
                - market: MARKET      - 市场类型
                - code: str           - 股票代码
                - name: str           - 股票名称
                - open: float         - 今开
                - high: float         - 最高
                - low: float          - 最低
                - close: float        - 现价
                - pre_close: float    - 昨收
                - server_time: str    - 服务器时间
                - vol: int            - 总量
                - cur_vol: int        - 现量
                - amount: int         - 总金额
                - in_vol: int         - 内盘
                - out_vol: int        - 外盘
                - handicap: Dict      - 1档盘口
                    - bid: list[dict] - 买盘
                    - ask: list[dict] - 卖盘
                - rise_speed: int     - 涨速
                - short_turnover: int - 短换手
                - min2_amount: int    - 2分钟金额
                - opening_rush: int   - 开盘抢筹
                - vol_rise_speed: int - 量涨速
                - depth: int          - 委比
                - active: int         - 活跃度
        '''
        return self.q_client().get_stock_quotes_list(category, start, count, sort_type, reverse, filter_types)

    def stock_quotes(self, code_list, code=None) -> list[dict]:
        '''
        获取股票报价
        支持三种形式的参数
        stock_quotes(market, code)
        stock_quotes((market, code))
        stock_quotes([(market1, code1), (market2, code2)])
        Args:
            code_list: MARKET | list[tuple[MARKET, str]] - 股票列表
            code: str   - 股票代码
        Return:
            List[Dict]: 同 stock_quotes_list（1档盘口）
        '''
        return self.q_client().get_quotes(code_list, code)

    def stock_unusual(self, market: MARKET, start: int = 0, count: int = 0) -> list[dict]:
        '''
        获取异动数据
        Args:
            market: MARKET - 市场类型
            start: int      - 起始位置，默认为0
            count: int      - 获取数量，默认为0（获取全部）
        Return:
            List[Dict]: 异动信息列表，每个元素包含：
                - index: int     - 序号
                - market: MARKET - 市场类型
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
            market: MARKET - 市场类型
            code: str      - 股票代码
        Return:
            List[Dict]: 竞价列表，每个元素包含：
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
            market: MARKET - 市场类型
            code: str      - 股票代码
            date: date     - 日期
        Return:
            List[Dict]: 委托列表，每个元素包含：
                - price: float  - 价格
                - vol: int      - 成交量
        '''
        return self.q_client().get_history_orders(market, code, date)

    def stock_transaction(self, market: MARKET, code: str, date: date = None) -> list[dict]:
        '''
        获取成交数据（实时或历史）
        Args:
            market: MARKET - 市场类型
            code: str      - 股票代码
            date: date     - 日期，默认为None（获取实时成交数据）
        Return:
            List[Dict]: 成交列表，每个元素包含：
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
            market: MARKET - 市场类型
            code: str      - 股票代码
        Return:
            List[float]: 价格列表
        '''
        return self.q_client().get_chart_sampling(market, code)

    def stock_f10(self, market: MARKET, code: str) -> list[dict]:
        '''
        获取F10数据（公司信息/除权分红/财报）
        Args:
            market: MARKET - 市场类型
            code: str      - 股票代码
        Return:
            List[Dict]: 公司信息列表，每个元素包含：
                - name: str              - 信息类别名称
                - content: str | dict    - 信息内容
        '''
        return self.q_client().get_company_info(market, code)

    def stock_block(self, block_type: BLOCK_FILE_TYPE) -> list[dict]:
        '''
        获取板块信息
        Args:
            block_type: BLOCK_FILE_TYPE - 板块文件类型
        Return:
            List[Dict]: 板块列表，每个元素包含：
                - block_name: str   - 板块名称
                - stocks: list[str] - 股票代码列表
        '''
        return self.q_client().get_block_file(block_type)

    # ── 扩展市场 (ExQuotationClient) ──────────────────────

    def goods_count(self) -> int:
        '''
        获取扩展市场商品数量
        Return:
            int - 商品数量
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

    def goods_list(self, start=0, count=2000) -> list[dict]:
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

    def goods_quotes_list(self, market: EX_MARKET, start: int = 0, count: int = 100, sort_type: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False) -> list[dict]:
        '''
        获取期货商品行情列表
        Args:
            market: EX_MARKET     - 扩展市场
            start: int            - 起始位置
            count: int            - 获取数量
            sort_type: SORT_TYPE   - 排序类型
            reverse: bool         - 倒序排序
        Return:
            List[Dict]: 同 goods_quotes（含5档盘口）
        '''
        return self.eq_client().get_quotes_list(market, start, count, sort_type, reverse)

    def goods_quotes(self, code_list, code=None) -> list[dict]:
        '''
        获取多个期货商品行情
        支持三种形式的参数
        goods_quotes(market, code)
        goods_quotes((market, code))
        goods_quotes([(market1, code1), (market2, code2)])
        Args:
            code_list: EX_MARKET | list[tuple[EX_MARKET, str]] - 商品列表
            code: str   - 商品代码
        Return:
            List[Dict]: 商品行情列表，每个元素包含：
                - market: EX_MARKET - 扩展市场
                - code: str         - 商品代码
                - open: float       - 今开
                - high: float       - 最高
                - low: float        - 最低
                - close: float      - 现价
                - open_position: int    - 开仓量
                - add_position: int     - 平仓量
                - hold_position: int    - 持仓量
                - vol: int              - 总量
                - cur_vol: int          - 现量
                - amount: int           - 总金额
                - in_vol: int           - 内盘
                - out_vol: int          - 外盘
                - handicap: Dict        - 5档盘口
                    - bid: list[dict]   - 买盘
                    - ask: list[dict]   - 卖盘
                - settlement: float     - 结算价
                - avg: float            - 均价
                - pre_settlement: float - 昨结算价
                - pre_close: float      - 昨收
                - pre_vol: int          - 昨总量
                - day3_raise: float     - 3日涨幅
                - date: date            - 日期
                - rise_speed: float     - 涨速
                - active: int           - 活跃度
        '''
        return self.eq_client().get_quotes(code_list, code)

    def goods_kline(self, market: EX_MARKET, code: str, period: PERIOD, start: int = 0, count: int = 800, times: int = 1) -> list[dict]:
        '''
        获取商品K线图
        Args:
            market: EX_MARKET       - 扩展市场
            code: str               - 商品代码
            period: PERIOD          - K线周期
            start: int              - 起始位置，默认为0
            count: int              - 获取数量，默认为800
            times: int              - 多周期倍数，默认为1
        Returns:
            List[Dict]: K线数据列表，每个元素包含：
                - datetime: datetime    - 时间
                - open: float           - 开盘价
                - high: float           - 最高价
                - low: float            - 最低价
                - close: float          - 收盘价
                - vol: int              - 成交量
                - amount: float         - 成交额
        '''
        return self.eq_client().get_kline(market, code, period, start, count, times)

    def goods_history_transaction(self, market: EX_MARKET, code: str, date: date) -> list[dict]:
        '''
        获取商品历史成交
        Args:
            market: EX_MARKET   - 扩展市场
            code: str           - 商品代码
            date: date          - 日期
        Return:
            List[Dict]: 成交列表，每个元素包含：
                - time: time    - 时间
                - price: float  - 价格
                - vol: int      - 成交量
                - action: str   - 成交方向（SELL，BUY，NEUTRAL）
        '''
        return self.eq_client().get_history_transaction(market, code, date)

    def goods_tick_chart(self, market: EX_MARKET, code: str, date: date = None) -> list[dict]:
        '''
        获取商品分时图
        Args:
            market: EX_MARKET   - 扩展市场
            code: str           - 商品代码
            date: date          - 日期，默认为None（查询当日分时图）
        Return:
            List[Dict]: 分时数据列表，每个元素包含：
                - time: time    - 时间
                - price: float  - 价格
                - avg: float    - 均价
                - vol: int      - 成交量
        '''
        return self.eq_client().get_tick_chart(market, code, date)

    def goods_chart_sampling(self, market: EX_MARKET, code: str) -> list[float]:
        '''
        获取商品分时图缩略
        Args:
            market: EX_MARKET       - 扩展市场
            code: str               - 商品代码
        Return:
            List[float]             - 价格列表
        '''
        return self.eq_client().get_chart_sampling(market, code)

    # ── MAC协议 (MacQuotationClient) ──────────────────────

    def board_count(self, market: BOARD_TYPE | EX_BOARD_TYPE) -> int:
        '''
        获取板块数量
        Args:
            market: BOARD_TYPE | EX_BOARD_TYPE - 板块类型
                BOARD_TYPE: A股板块 (HY: 行业, GN: 概念, FG: 风格, DQ: 地区)
                EX_BOARD_TYPE: 扩展板块 (HK_ALL, US_ALL 等)
        Return:
            int - 板块数量
        '''
        return self._mac_for(market).get_board_count(market)

    def board_list(self, market: BOARD_TYPE | EX_BOARD_TYPE, count: int = 10000) -> list[dict]:
        '''
        获取板块列表
        Args:
            market: BOARD_TYPE | EX_BOARD_TYPE - 板块类型
            count: int - 获取数量，默认10000
        Return:
            List[Dict]: 板块列表，每个元素包含：
                - code: str    - 板块代码
                - name: str    - 板块名称
        '''
        return self._mac_for(market).get_board_list(market, count)

    def board_members(self, board_symbol: str, count: int = 10000) -> list[dict]:
        '''
        获取板块成员
        Args:
            board_symbol: str - 板块代码
            count: int        - 获取数量，默认10000
        Return:
            List[Dict]: 板块成员列表
        '''
        return self.mac_client().get_board_members(board_symbol, count)

    def board_members_quotes(self, board_symbol: str, count: int = 10000) -> list[dict]:
        '''
        获取板块成分报价
        Args:
            board_symbol: str - 板块代码
            count: int        - 获取数量，默认10000
        Return:
            List[Dict]: 板块成分报价列表
        '''
        return self.mac_client().get_board_members_quotes(board_symbol, count)

    def board_belong(self, symbol: str, market: MARKET) -> list[dict]:
        '''
        查询股票所属板块
        Args:
            symbol: str   - 股票代码
            market: MARKET - 市场类型
        Return:
            List[Dict]: 所属板块列表
        '''
        return self.mac_client().get_symbol_belong_board(symbol, market)

    def symbol_bars(self, market, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800, adjust: ADJUST = ADJUST.NONE) -> list[dict]:
        '''
        获取K线数据(MAC协议，支持A股/港股/美股)
        Args:
            market: MARKET | EX_MARKET - 市场类型
            code: str       - 股票/商品代码
            period: PERIOD  - K线周期
            times: int      - 多周期倍数，默认为1
            start: int      - 起始位置，默认为0
            count: int      - 获取数量，默认为800
            adjust: ADJUST  - 复权类型
        Returns:
            List[Dict]: K线数据列表
        '''
        return self._mac_for(market).get_symbol_bars(market, code, period, times, start, count, adjust)

    def mac_server_init(self) -> bool:
        '''
        MAC协议服务器初始化/订阅
        Return:
            bool - 是否成功
        '''
        return self.mac_client().server_init()

    def mac_file_list(self, filename: str, offset: int = 0) -> dict:
        '''
        查询文件列表信息
        Args:
            filename: str - 文件名
            offset: int   - 偏移量
        Return:
            Dict: offset/size/hash 等信息
        '''
        return self.mac_client().get_file_list(filename, offset)

    def mac_download_file(self, filename: str, index: int = 1, offset: int = 0, size: int = 30000) -> dict:
        '''
        下载文件内容
        Args:
            filename: str - 文件名
            index: int    - 索引，默认1
            offset: int   - 偏移量
            size: int     - 大小，默认30000
        Return:
            Dict: index/size/content
        '''
        return self.mac_client().download_file(filename, index, offset, size)

    def mac_stock_query(self, market: MARKET, code: str, flag: int = 1, unk: int = 0) -> dict:
        '''
        查询股票行情信息
        Args:
            market: MARKET - 市场类型
            code: str      - 股票代码
            flag: int      - 标志位
            unk: int       - 未知参数
        Return:
            Dict: 股票行情 (market/code/name/pre_close/open/high/low/close)
        '''
        return self.mac_client().get_stock_query(market, code, flag, unk)

    def mac_batch_stock_data(self, market: MARKET, code: str) -> dict:
        '''
        获取批量股票数据(OHLCV)
        Args:
            market: MARKET - 市场类型
            code: str      - 股票代码
        Return:
            Dict: 股票数据 (market/code/name/open/high/low/close)
        '''
        return self.mac_client().get_batch_stock_data(market, code)

    def mac_stock_detail(self, market: MARKET, code: str) -> list:
        '''
        获取股票分笔明细(tick数据)
        Args:
            market: MARKET - 市场类型
            code: str      - 股票代码
        Return:
            List[Dict]: 分笔明细列表 (time/price/vol/direction)
        '''
        return self.mac_client().get_stock_detail(market, code)

    def mac_stock_bar_count(self, market: MARKET, code: str, count: int = 500) -> list:
        '''
        获取股票K线柱数据
        Args:
            market: MARKET - 市场类型
            code: str      - 股票代码
            count: int     - 获取数量，默认500
        Return:
            List[Dict]: K线柱数据 (offset/price/vol/change)
        '''
        return self.mac_client().get_stock_bar_count(market, code, count)

    def mac_stock_small_info(self, market: MARKET, code: str, period: int = 5, flag: int = 1) -> list:
        '''
        获取股票分钟级数据
        Args:
            market: MARKET - 市场类型
            code: str      - 股票代码
            period: int    - 周期(分钟)，默认5
            flag: int      - 标志位，默认1
        Return:
            List[Dict]: 分钟级数据 (index/price/avg/vol)
        '''
        return self.mac_client().get_stock_small_info(market, code, period, flag)

    def mac_kline_offset(self, offset: int = 0, count: int = 128000) -> list:
        '''
        获取K线偏移表(股票/指数列表)
        Args:
            offset: int - 偏移量，默认0
            count: int  - 获取数量，默认128000
        Return:
            List[Dict]: 股票/指数列表 (market/code/name)
        '''
        return self.mac_client().get_kline_offset(offset, count)


if __name__ == '__main__':
    import pandas as pd

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
        print(pd.DataFrame(client.stock_quotes_list(CATEGORY.A, count = 0, sort_type=SORT_TYPE.TOTAL_AMOUNT)))
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
        print(pd.DataFrame(client.goods_quotes_list(EX_MARKET.US_STOCK, sort_type=SORT_TYPE.TOTAL_AMOUNT)))
        print(pd.DataFrame([client.goods_quotes(EX_MARKET.US_STOCK, 'TSLA')]))
        print(pd.DataFrame(client.goods_quotes([(EX_MARKET.US_STOCK, 'TSLA'), (EX_MARKET.HK_MAIN_BOARD, '09988')])))
        print(pd.DataFrame(client.goods_kline(EX_MARKET.US_STOCK, 'TSLA', PERIOD.DAILY)))
        print(pd.DataFrame(client.goods_history_transaction(EX_MARKET.US_STOCK, 'TSLA', date(2026, 3, 3))))
        print(pd.DataFrame(client.goods_tick_chart(EX_MARKET.US_STOCK, 'TSLA')))
        print(pd.DataFrame(client.goods_tick_chart(EX_MARKET.US_STOCK, 'TSLA', date(2026, 3, 3))))
        print(pd.DataFrame(client.goods_chart_sampling(EX_MARKET.US_STOCK, 'TSLA')))
