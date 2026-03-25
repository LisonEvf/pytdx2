from datetime import date

from client.exQuotationClient import exQuotationClient
from client.quotationClient import QuotationClient
from mcp.server.fastmcp import FastMCP

from const import CATEGORY, EX_CATEGORY, MARKET, PERIOD

mcp = FastMCP('TDX MCP Server')

quotationClient = QuotationClient(True, True)
ex_quotation_client = exQuotationClient(True, True)

def hq():
    if not quotationClient.connected:
        quotationClient.connect().login()
    return quotationClient

def ex_hq():
    if not ex_quotation_client.connected:
        ex_quotation_client.connect().login()
    return ex_quotation_client

@mcp.tool()
def get_Index_Overview():
    ''' 获取指数概况
    :return: 上证、深证、北证、创业、科创、沪深指数数据的JSON字符串
    '''
    return hq().get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001'), (MARKET.SZ, '399006'), (MARKET.BJ, '899050'), (MARKET.SH, '000688'), (MARKET.SH, '000300')])

@mcp.tool()
def stock_quotes(code_list: MARKET | list[tuple[MARKET, str]], code: str = None):
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
    return hq().get_quotes(code_list, code)

@mcp.tool()
def stock_kline(market: MARKET, code: str, period: PERIOD, start = 0, count = 800, times: int = 1):
    '''
    获取K线数据
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
    return hq().get_kline(market, code, period, start, count, times)

@mcp.tool()
def stock_tick_chart(market: MARKET, code: str, date: date = None, start: int = 0, count: int = 0xba00) -> list[dict]:
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
        return hq().get_tick_chart(market, code, date, start, count)

@mcp.tool()
def stock_top_board(category: CATEGORY = CATEGORY.A):
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
    return hq().get_stock_top_board(category)

@mcp.tool()
def stock_quotes_list(category: CATEGORY, start:int = 0, count: int = 80, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False, filter: list[FILTER_TYPE] = []) -> list[dict]:
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
        return hq().get_stock_quotes_list(category, start, count, sortType, reverse, filter)

@mcp.tool()
def stock_quotes(code_list: MARKET | list[tuple[MARKET, str]], code: str = None) -> list[dict]:
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
        return hq().get_quotes(code_list, code)

@mcp.tool()
def stock_unusual(market: MARKET, start: int = 0, count: int = 0) -> list[dict]:
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
    return hq().get_unusual(market, start, count)

@mcp.tool()
def stock_auction(market: MARKET, code: str) -> list[dict]:
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
    return hq().get_auction(market, code)

@mcp.tool()
def stock_transaction(market: MARKET, code: str, date: date = None) -> list[dict]:
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
    return hq().get_transaction(market, code, date)

@mcp.tool()
def stock_f10(market: MARKET, code: str) -> list[dict]:
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
    return hq().get_company_info(market, code)

@mcp.tool()
def goods_quotes_list(category: EX_CATEGORY, start: int = 0, count: int = 100, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False) -> list[dict]:
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
    return ex_hq().get_quotes_list(category, start, count, sortType, reverse)

@mcp.tool()
def goods_quotes(code_list: EX_CATEGORY | list[tuple[EX_CATEGORY, str]], code = None) -> list[dict]:
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
    return ex_hq().get_quotes(code_list, code)

@mcp.tool()
def goods_kline(category: EX_CATEGORY, code: str, period: PERIOD, start: int = 0, count: int = 800, times: int = 1) -> list[dict]:
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
    return ex_hq().get_kline(category, code, period, start, count, times)

@mcp.tool()
def goods_history_transaction(category: EX_CATEGORY, code: str, date: date) -> list[dict]:
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
    return ex_hq().get_history_transaction(category, code, date)

@mcp.tool()
def goods_tick_chart(category: EX_CATEGORY, code: str, date: date = None) -> list[dict]:
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
    return ex_hq().get_tick_chart(category, code, date)


if __name__ == '__main__':
    mcp.run()