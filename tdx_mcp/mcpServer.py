import json
from datetime import date as date_type
from datetime import datetime

from tdx_mcp.client.exQuotationClient import exQuotationClient
from tdx_mcp.client.quotationClient import QuotationClient
from mcp.server.fastmcp import FastMCP

from tdx_mcp.const import CATEGORY, EX_CATEGORY, FILTER_TYPE, MARKET, PERIOD, SORT_TYPE

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

# MARKET: 0=深圳, 1=上海, 2=北交所
_MARKET_DESC = "市场代码: 0=深圳(SZ), 1=上海(SH), 2=北交所(BJ)"

# CATEGORY: 0=上证A, 2=深证A, 6=A股, 7=B股, 8=科创板, 12=北证A, 14=创业板
_CATEGORY_DESC = "市场分类: 0=上证A(SH), 2=深证A(SZ), 6=A股, 7=B股, 8=科创板(KCB), 12=北证A(BJ), 14=创业板(CYB)"

# PERIOD: 0=5分钟, 1=15分钟, 2=30分钟, 3=60分钟, 4=日线, 5=周线, 6=月线, 7=1分钟, 8=多分钟, 9=多日, 10=季线, 11=年线, 13=多秒
_PERIOD_DESC = "K线周期: 7=1分钟, 0=5分钟, 1=15分钟, 2=30分钟, 3=60分钟, 4=日线, 5=周线, 6=月线, 10=季线, 11=年线"

# FILTER_TYPE: 1=次新股, 2=科创板, 4=ST, 8=创业板, 16=北证 (可组合如 10=科创板+创业板)
_FILTER_DESC = "过滤类型(可组合): 1=次新股(NEW), 2=科创板(KC), 4=ST(ST), 8=创业板(CY), 16=北证(BJ)"

# SORT_TYPE
_SORT_DESC = """排序类型: 0=代码, 6=现价, 14=涨幅%, 15=振幅%, 34=换手%, 35=量比, 224=涨速%, 22=委比%, 9=总量, 10=总金额"""

# EX_CATEGORY
_EX_CATEGORY_DESC = """扩展市场类别: 28=郑州商品, 29=大连商品, 30=上海期货, 47=中金所期货, 31=香港主板, 71=港股, 16=纽约COMEX, 17=纽约NYMEX, 18=芝加哥CBOT"""

_DATE_DESC = "日期，格式: YYYY-MM-DD（如 2024-01-15）"

# ============ Resources ============

@mcp.resource("config://markets")
def resource_markets() -> str:
    """市场代码配置"""
    return json.dumps({
        "0": {"name": "深圳", "code": "SZ"},
        "1": {"name": "上海", "code": "SH"},
        "2": {"name": "北交所", "code": "BJ"}
    }, ensure_ascii=False, indent=2)

@mcp.resource("config://categories")
def resource_categories() -> str:
    """股票分类配置"""
    return json.dumps({
        "0": "上证A", "2": "深证A", "6": "A股",
        "7": "B股", "8": "科创板", "12": "北证A", "14": "创业板"
    }, ensure_ascii=False, indent=2)

@mcp.resource("config://periods")
def resource_periods() -> str:
    """K线周期配置"""
    return json.dumps({
        "7": "1分钟", "0": "5分钟", "1": "15分钟",
        "2": "30分钟", "3": "60分钟", "4": "日线",
        "5": "周线", "6": "月线", "10": "季线", "11": "年线"
    }, ensure_ascii=False, indent=2)

@mcp.resource("config://ex_categories")
def resource_ex_categories() -> str:
    """扩展市场类别（期货/港股等）"""
    return json.dumps({
        "28": "郑州商品", "29": "大连商品", "30": "上海期货",
        "47": "中金所期货", "31": "香港主板", "71": "港股",
        "16": "纽约COMEX", "17": "纽约NYMEX", "18": "芝加哥CBOT"
    }, ensure_ascii=False, indent=2)

@mcp.resource("config://sort_types")
def resource_sort_types() -> str:
    """排序类型配置"""
    return json.dumps({
        "0": "代码", "6": "现价", "14": "涨幅%", "15": "振幅%",
        "34": "换手%", "35": "量比", "224": "涨速%", "22": "委比%",
        "9": "总量", "10": "总金额"
    }, ensure_ascii=False, indent=2)

@mcp.resource("config://filter_types")
def resource_filter_types() -> str:
    """过滤类型配置（可组合使用，如 10=科创板+创业板）"""
    return json.dumps({
        "1": "次新股", "2": "科创板", "4": "ST", "8": "创业板", "16": "北证"
    }, ensure_ascii=False, indent=2)

# ============ Tools ============

def parse_date(date_str: str | None) -> date_type | None:
    """将日期字符串转换为date对象"""
    if date_str is None:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d").date()

@mcp.tool()
def get_index_overview():
    ''' 获取指数概况
    :return: 上证、深证、北证、创业、科创、沪深指数数据的JSON字符串
    '''
    return hq().get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001'), (MARKET.SZ, '399006'), (MARKET.BJ, '899050'), (MARKET.SH, '000688'), (MARKET.SH, '000300')])

@mcp.tool()
def stock_kline(market: int, code: str, period: int, adjust_type: str = "none", start = 0, count = 800, times: int = 1):
    '''
    获取K线数据（支持复权和换手率）
        Args:
            market: int       - ''' + _MARKET_DESC + '''
            code: str         - 股票代码(如 000001)
            period: int       - ''' + _PERIOD_DESC + '''
            adjust_type: str  - 复权类型: none=不复权(默认), qfq=前复权, hfq=后复权
            start: int        - 起始位置，默认为0
            count: int        - 获取数量，默认为800
            times: int        - 多周期倍数，默认为1（配合period=8/9/13使用）
        Returns:
            Dict: {
                "data": K线数据列表，每个元素包含：
                    - datetime: datetime    - 时间
                    - open: float           - 开盘价
                    - high: float           - 最高价
                    - low: float            - 最低价
                    - close: float          - 收盘价
                    - vol: int              - 成交量
                    - amount: int           - 成交额
                    - turnover: float       - 换手率(%)
                    - adjust_factor?: float - 复权因子（复权时）
                    - up_count?: int        - 上涨数（指数专有）
                    - down_count?: int      - 下跌数（指数专有）
                "float_shares": float       - 流通股本(万股)
                "warning?: str              - 可选警告信息
            }
    '''
    # 验证 adjust_type
    if adjust_type not in ["none", "qfq", "hfq"]:
        return {"data": [], "error": f"无效的复权类型: {adjust_type}，支持: none/qfq/hfq"}

    return hq().get_kline(MARKET(market), code, PERIOD(period), adjust_type, start, count, times)

@mcp.tool()
def stock_tick_chart(market: int, code: str, date: str = None, start: int = 0, count: int = 0xba00) -> list[dict]:
    '''
    获取分时图
        Args:
            market: int - ''' + _MARKET_DESC + '''
            code: str   - 股票代码
            date: str   - ''' + _DATE_DESC + '''，默认为None（查询当日）
            start: int  - 起始位置，默认为0
            count: int  - 获取数量，默认为47744
        Returns:
            List[Dict]: 分时数据列表，每个元素包含：
                - price: float - 成交价
                - avg: float   - 平均价
                - vol: int     - 成交量
    '''
    return hq().get_tick_chart(MARKET(market), code, parse_date(date), start, count)

@mcp.tool()
def stock_top_board(category: int = 6):
    '''
    获取股票排行榜
        Args:
            category: int - ''' + _CATEGORY_DESC + '''，默认6(A股)
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
    return hq().get_stock_top_board(CATEGORY(category))

@mcp.tool()
def stock_quotes_list(category: int, start:int = 0, count: int = 80, sortType: int = 0, reverse: bool = False, filter: list[int] = []) -> list[dict]:
    '''
    获取各类股票行情列表
        Args:
            category: int        - ''' + _CATEGORY_DESC + '''
            start: int           - 起始位置
            count: int           - 获取数量
            sortType: int        - ''' + _SORT_DESC + '''
            reverse: bool        - 倒序排序
            filter: list[int]    - ''' + _FILTER_DESC + '''
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
                - vol: int            - 总量
                - cur_vol: int        - 现量
                - amount: int         - 总金额
                - turnover: float     - 换手率(%)
                - handicap: Dict      - 1档盘口
                - rise_speed: int     - 涨速
                - depth: int          - 委比
                - active: int         - 活跃度
    '''
    filter_types = [FILTER_TYPE(f) for f in filter] if filter else []
    return hq().get_stock_quotes_list(CATEGORY(category), start, count, SORT_TYPE(sortType), reverse, filter_types)

@mcp.tool()
def stock_quotes(code_list: int | list[tuple[int, str]], code: str = None) -> list[dict]:
    '''
    获取股票报价
    支持三种形式: stock_quotes(market, code), stock_quotes((market, code)), stock_quotes([(market1, code1), (market2, code2)])
        Args:
            code_list: int或元组列表 - ''' + _MARKET_DESC + '''
            code: str               - 股票代码（当code_list为market时使用）
        Return:
            List[Dict]: 股票报价列表，每个元素包含：
                - market: MARKET      - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
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
                - turnover: float     - 换手率(%)
                - handicap: Dict      - 1档盘口
                - rise_speed: int     - 涨速
                - depth: int          - 委比
                - active: int         - 活跃度
    '''
    if isinstance(code_list, int):
        return hq().get_quotes(MARKET(code_list), code)
    elif isinstance(code_list, list):
        converted = [(MARKET(m), c) for m, c in code_list]
        return hq().get_quotes(converted, code)
    return hq().get_quotes(code_list, code)

@mcp.tool()
def stock_unusual(market: int, start: int = 0, count: int = 0) -> list[dict]:
    '''
    获取异动数据
        Args:
            market: int - ''' + _MARKET_DESC + '''
            start: int  - 起始位置，默认为0
            count: int  - 获取数量，默认为0（获取全部）
        Return:
            List[Dict]: 异动数据列表，每个元素包含：
            - index: int     - 序号
            - market: MARKET - 市场类型 (SZ: 深圳, SH: 上海, BJ: 北交所)
            - code: str      - 股票代码
            - time: time     - 时间
            - desc: str      - 异动类型
            - value: str     - 异动值
    '''
    return hq().get_unusual(MARKET(market), start, count)

@mcp.tool()
def stock_auction(market: int, code: str) -> list[dict]:
    '''
    获取竞价数据
        Args:
            market: int - ''' + _MARKET_DESC + '''
            code: str   - 股票代码
        Return:
            List[Dict]: 竞价数据列表，每个元素包含：
            - time: time        - 时间
            - price: float      - 撮合价
            - matched: int      - 匹配量
            - unmatched: int    - 未匹配量
    '''
    return hq().get_auction(MARKET(market), code)

@mcp.tool()
def stock_transaction(market: int, code: str, date: str = None) -> list[dict]:
    '''
    获取历史成交数据
        Args:
            market: int - ''' + _MARKET_DESC + '''
            code: str   - 股票代码
            date: str   - ''' + _DATE_DESC + '''，默认为None（获取实时）
        Return:
            List[Dict]: 成交数据列表，每个元素包含：
            - time: time        - 时间
            - price: float      - 价格
            - vol: int          - 成交量
            - trans: int        - 成交笔数
            - action: str       - 成交方向（SELL，BUY，NEUTRAL）
    '''
    return hq().get_transaction(MARKET(market), code, parse_date(date))

@mcp.tool()
def stock_f10(market: int, code: str) -> list[dict]:
    '''
    获取F10数据（公司信息）
        Args:
            market: int - ''' + _MARKET_DESC + '''
            code: str   - 股票代码
        Return:
            List[Dict]: 公司信息列表
    '''
    return hq().get_company_info(MARKET(market), code)

@mcp.tool()
def goods_quotes_list(category: int, start: int = 0, count: int = 100, sortType: int = 0, reverse: bool = False) -> list[dict]:
    '''
    获取期货商品行情列表
        Args:
            category: int  - ''' + _EX_CATEGORY_DESC + '''
            start: int     - 起始位置
            count: int     - 获取数量
            sortType: int  - ''' + _SORT_DESC + '''
            reverse: bool  - 倒序排序
        Return:
            List[Dict]: 商品行情列表，每个元素包含：
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
    return ex_hq().get_quotes_list(EX_CATEGORY(category), start, count, SORT_TYPE(sortType), reverse)

@mcp.tool()
def goods_quotes(code_list: int | list[tuple[int, str]], code = None) -> list[dict]:
    '''
    获取多个期货商品行情
    支持三种形式: goods_quotes(category, code), goods_quotes((category, code)), goods_quotes([(category1, code1), (category2, code2)])
        Args:
            code_list: int或元组列表 - ''' + _EX_CATEGORY_DESC + '''
            code: str               - 商品代码（当code_list为category时使用）
        Return:
            List[Dict]: 商品报价列表，每个元素包含：
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
    if isinstance(code_list, int):
        return ex_hq().get_quotes(EX_CATEGORY(code_list), code)
    elif isinstance(code_list, list):
        converted = [(EX_CATEGORY(c), code_item) for c, code_item in code_list]
        return ex_hq().get_quotes(converted, code)
    return ex_hq().get_quotes(code_list, code)

@mcp.tool()
def goods_kline(category: int, code: str, period: int, start: int = 0, count: int = 800, times: int = 1) -> list[dict]:
    '''
    获取商品K线图
        Args:
            category: int - ''' + _EX_CATEGORY_DESC + '''
            code: str     - 商品代码
            period: int   - ''' + _PERIOD_DESC + '''
            start: int    - 起始位置，默认为0
            count: int    - 获取数量，默认为800
            times: int    - 多周期倍数，默认为1
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
    return ex_hq().get_kline(EX_CATEGORY(category), code, PERIOD(period), start, count, times)

@mcp.tool()
def goods_history_transaction(category: int, code: str, date: str) -> list[dict]:
    '''
    获取商品历史成交
        Args:
            category: int - ''' + _EX_CATEGORY_DESC + '''
            code: str     - 商品代码
            date: str     - ''' + _DATE_DESC + '''
        Return:
            List[Dict]: 历史成交列表，每个元素包含：
            - time: time        - 时间
            - price: float      - 价格
            - vol: int          - 成交量
            - action: str       - 成交方向（SELL，BUY，NEUTRAL）
    '''
    return ex_hq().get_history_transaction(EX_CATEGORY(category), code, parse_date(date))

@mcp.tool()
def goods_tick_chart(category: int, code: str, date: str = None) -> list[dict]:
    '''
    获取商品分时图
        Args:
            category: int - ''' + _EX_CATEGORY_DESC + '''
            code: str     - 商品代码
            date: str     - ''' + _DATE_DESC + '''，默认为None（查询当日）
        Return:
            List[Dict]: 分时数据列表，每个元素包含：
            - time: time        - 时间
            - price: float      - 价格
            - avg: float        - 均价
            - vol: int          - 成交量
    '''
    return ex_hq().get_tick_chart(EX_CATEGORY(category), code, parse_date(date))


# ============ 指标计算工具 ============

@mcp.tool()
def indicator_ma(kline_data: list[dict], periods: list[int] = [5, 10, 20, 60]) -> dict[str, list]:
    '''
    计算移动平均线 MA
        Args:
            kline_data: list[dict] - K线数据（需包含 close 字段）
            periods: list[int] - 周期列表，默认 [5, 10, 20, 60]
        Returns:
            Dict[str, list]: 各周期的MA值，键为 "MA5", "MA10" 等
    '''
    closes = [k['close'] for k in kline_data]
    result = {}
    for p in periods:
        ma_values = []
        for i in range(len(closes)):
            if i < p - 1:
                ma_values.append(None)
            else:
                ma_values.append(round(sum(closes[i-p+1:i+1]) / p, 2))
        result[f'MA{p}'] = ma_values
    return result

@mcp.tool()
def indicator_ema(kline_data: list[dict], periods: list[int] = [12, 26]) -> dict[str, list]:
    '''
    计算指数移动平均 EMA
        Args:
            kline_data: list[dict] - K线数据（需包含 close 字段）
            periods: list[int] - 周期列表，默认 [12, 26]
        Returns:
            Dict[str, list]: 各周期的EMA值
    '''
    closes = [k['close'] for k in kline_data]
    result = {}
    for p in periods:
        ema_values = []
        multiplier = 2 / (p + 1)
        for i, close in enumerate(closes):
            if i == 0:
                ema_values.append(close)
            else:
                ema_values.append(round((close - ema_values[-1]) * multiplier + ema_values[-1], 2))
        result[f'EMA{p}'] = ema_values
    return result

@mcp.tool()
def indicator_macd(kline_data: list[dict], fast: int = 12, slow: int = 26, signal: int = 9) -> dict[str, list]:
    '''
    计算 MACD 指标
        Args:
            kline_data: list[dict] - K线数据（需包含 close 字段）
            fast: int - 快线周期，默认12
            slow: int - 慢线周期，默认26
            signal: int - 信号线周期，默认9
        Returns:
            Dict[str, list]: 包含 DIF, DEA, MACD 三条线
    '''
    closes = [k['close'] for k in kline_data]

    def calc_ema(data, period):
        result = []
        multiplier = 2 / (period + 1)
        for i, val in enumerate(data):
            if i == 0:
                result.append(val)
            else:
                result.append((val - result[-1]) * multiplier + result[-1])
        return result

    ema_fast = calc_ema(closes, fast)
    ema_slow = calc_ema(closes, slow)
    dif = [round(f - s, 4) for f, s in zip(ema_fast, ema_slow)]

    dea = calc_ema(dif, signal)
    dea = [round(d, 4) for d in dea]

    macd = [round((d - e) * 2, 4) for d, e in zip(dif, dea)]

    return {'DIF': dif, 'DEA': dea, 'MACD': macd}

@mcp.tool()
def indicator_rsi(kline_data: list[dict], period: int = 14) -> list[float | None]:
    '''
    计算 RSI 相对强弱指标
        Args:
            kline_data: list[dict] - K线数据（需包含 close 字段）
            period: int - 周期，默认14
        Returns:
            List[float | None]: RSI值列表（0-100）
    '''
    closes = [k['close'] for k in kline_data]
    rsi_values = []

    for i in range(len(closes)):
        if i < period:
            rsi_values.append(None)
        else:
            gains = []
            losses = []
            for j in range(i - period + 1, i + 1):
                change = closes[j] - closes[j - 1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period

            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi_values.append(round(100 - (100 / (1 + rs)), 2))

    return rsi_values

@mcp.tool()
def indicator_kdj(kline_data: list[dict], n: int = 9, m1: int = 3, m2: int = 3) -> dict[str, list]:
    '''
    计算 KDJ 指标
        Args:
            kline_data: list[dict] - K线数据（需包含 high, low, close 字段）
            n: int - RSV周期，默认9
            m1: int - K值平滑周期，默认3
            m2: int - D值平滑周期，默认3
        Returns:
            Dict[str, list]: 包含 K, D, J 三条线
    '''
    rsv_list = []
    for i in range(len(kline_data)):
        if i < n - 1:
            rsv_list.append(50.0)  # 默认值
        else:
            high_n = max(k['high'] for k in kline_data[i-n+1:i+1])
            low_n = min(k['low'] for k in kline_data[i-n+1:i+1])
            if high_n == low_n:
                rsv_list.append(50.0)
            else:
                rsv = (kline_data[i]['close'] - low_n) / (high_n - low_n) * 100
                rsv_list.append(round(rsv, 2))

    k_values = []
    d_values = []
    for i, rsv in enumerate(rsv_list):
        if i == 0:
            k_values.append(50.0)
            d_values.append(50.0)
        else:
            k = (2/3) * k_values[-1] + (1/3) * rsv
            d = (2/3) * d_values[-1] + (1/3) * k
            k_values.append(round(k, 2))
            d_values.append(round(d, 2))

    j_values = [round(3 * k - 2 * d, 2) for k, d in zip(k_values, d_values)]
    return {'K': k_values, 'D': d_values, 'J': j_values}

@mcp.tool()
def indicator_boll(kline_data: list[dict], period: int = 20, std_dev: float = 2.0) -> dict[str, list]:
    '''
    计算布林带 BOLL
        Args:
            kline_data: list[dict] - K线数据（需包含 close 字段）
            period: int - 周期，默认20
            std_dev: float - 标准差倍数，默认2.0
        Returns:
            Dict[str, list]: 包含 UPPER, MID, LOWER 三条线
    '''
    closes = [k['close'] for k in kline_data]
    import statistics

    upper, mid, lower = [], [], []
    for i in range(len(closes)):
        if i < period - 1:
            upper.append(None)
            mid.append(None)
            lower.append(None)
        else:
            window = closes[i-period+1:i+1]
            ma = sum(window) / period
            std = statistics.stdev(window)
            mid.append(round(ma, 2))
            upper.append(round(ma + std_dev * std, 2))
            lower.append(round(ma - std_dev * std, 2))

    return {'UPPER': upper, 'MID': mid, 'LOWER': lower}

@mcp.tool()
def indicator_atr(kline_data: list[dict], period: int = 14) -> list[float | None]:
    '''
    计算真实波动幅度 ATR
        Args:
            kline_data: list[dict] - K线数据（需包含 high, low, close 字段）
            period: int - 周期，默认14
        Returns:
            List[float | None]: ATR值列表
    '''
    tr_list = []
    for i in range(len(kline_data)):
        if i == 0:
            tr_list.append(kline_data[i]['high'] - kline_data[i]['low'])
        else:
            high = kline_data[i]['high']
            low = kline_data[i]['low']
            prev_close = kline_data[i-1]['close']
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(round(tr, 2))

    atr_values = []
    for i, tr in enumerate(tr_list):
        if i < period - 1:
            atr_values.append(None)
        elif i == period - 1:
            atr_values.append(round(sum(tr_list[:period]) / period, 2))
        else:
            atr_values.append(round((atr_values[-1] * (period - 1) + tr) / period, 2))

    return atr_values

@mcp.tool()
def indicator_vol_ma(kline_data: list[dict], periods: list[int] = [5, 10, 20]) -> dict[str, list]:
    '''
    计算成交量移动平均线
        Args:
            kline_data: list[dict] - K线数据（需包含 vol 字段）
            periods: list[int] - 周期列表，默认 [5, 10, 20]
        Returns:
            Dict[str, list]: 各周期的成交量MA值
    '''
    vols = [k['vol'] for k in kline_data]
    result = {}
    for p in periods:
        ma_values = []
        for i in range(len(vols)):
            if i < p - 1:
                ma_values.append(None)
            else:
                ma_values.append(round(sum(vols[i-p+1:i+1]) / p, 0))
        result[f'VOL_MA{p}'] = ma_values
    return result


# ============ 市场分析工具 ============

@mcp.tool()
def market_overview() -> dict:
    '''
    全市场概览 - 提供主要指数、涨跌分布、成交额等市场整体情况
        Returns:
            Dict: {
                "indices": [
                    {
                        "name": "上证指数",
                        "code": "999999",
                        "market": "SH",
                        "price": 3878.96,
                        "change": -1.07,
                        "change_pct": -0.03,
                        "volume": 340000000,
                        "amount": 49152000000
                    },
                    ...
                ],
                "breadth": {
                    "up": 21,         # 上涨家数
                    "down": 301,      # 下跌家数
                    "flat": 1,        # 平盘家数
                    "limit_up": 0,    # 涨停数
                    "limit_down": 0   # 跌停数
                },
                "amount": {
                    "sh": 4915.2,     # 上海成交额（亿）
                    "sz": 6568.8,     # 深圳成交额（亿）
                    "total": 11484    # 两市总成交额（亿）
                }
            }
    '''
    from tdx_mcp.tools.market_analysis import market_overview as _market_overview
    return _market_overview(hq())

@mcp.tool()
def sector_rotation() -> dict:
    '''
    板块轮动分析 - 显示领涨和领跌的行业板块
        Returns:
            Dict: {
                "top_gainers": [
                    {
                        "name": "信息技术",
                        "code": "399239",
                        "change_pct": 2.35
                    },
                    ...
                ],
                "top_losers": [
                    {
                        "name": "房地产",
                        "code": "399241",
                        "change_pct": -1.82
                    },
                    ...
                ],
                "all_sectors": [...]  # 所有板块按涨跌幅排序
            }
    '''
    from tdx_mcp.tools.market_analysis import sector_rotation as _sector_rotation
    return _sector_rotation(hq())

@mcp.tool()
def market_breadth() -> dict:
    '''
    市场广度分析 - 统计涨跌家数、涨跌幅分布、市场强度等
        Returns:
            Dict: {
                "up_count": 21,           # 上涨家数
                "down_count": 301,        # 下跌家数
                "flat_count": 1,          # 平盘家数
                "limit_up": 0,            # 涨停数
                "limit_down": 0,          # 跌停数
                "distribution": {
                    "above_5": 2,         # 涨幅>5%
                    "between_3_5": 5,     # 涨幅3-5%
                    "between_0_3": 14,    # 涨幅0-3%
                    "between_neg3_0": 180, # 跌幅0-3%
                    "between_neg5_neg3": 90, # 跌幅3-5%
                    "below_neg5": 31      # 跌幅<-5%
                },
                "strength": 0.065,        # 市场强度 = 上涨家数/总家数
                "breadth_ratio": 0.065    # 涨跌比
            }
    '''
    from tdx_mcp.tools.market_analysis import market_breadth as _market_breadth
    return _market_breadth(hq())

@mcp.tool()
def market_sentiment() -> dict:
    '''
    市场情绪分析 - 提供成交额、换手率、量比、市场热度等情绪指标
        Returns:
            Dict: {
                "total_amount": 11484,    # 两市总成交额（亿）
                "turnover_median": 2.35,  # 换手率中位数(%)
                "vol_ratio_avg": 1.05,    # 量比平均值
                "market_heat": "偏冷",    # 市场热度
                "heat_score": 25,         # 热度评分(0-100)
                "sentiment_indicators": {
                    "up_ratio": 0.065,    # 上涨比例
                    "limit_up_ratio": 0,  # 涨停比例
                    "turnover_level": "低", # 换手率水平
                    "amount_level": "缩量"  # 成交额水平
                }
            }
    '''
    from tdx_mcp.tools.market_analysis import market_sentiment as _market_sentiment
    return _market_sentiment(hq())

@mcp.tool()
def stock_detail(market: int, code: str) -> dict:
    '''
    个股详情 - 整合报价、F10数据、财务指标的个股全景分析
        Args:
            market: int - ''' + _MARKET_DESC + '''
            code: str   - 股票代码(如 000001)
        Returns:
            Dict: {
                "basic": {"name": "平安银行", "code": "000001", "market": "SZ", "industry": "银行"},
                "quote": {"price": 12.35, "change_pct": 1.23, "pe_ratio": 6.5, "pb_ratio": 0.8, "market_cap": 2400.5},
                "financial": {"eps": 1.85, "bvps": 15.23, "roe": 12.5, "total_shares": 194.05}
            }
    '''
    from tdx_mcp.tools.stock_analysis import stock_detail as _stock_detail
    return _stock_detail(hq(), MARKET(market), code)

@mcp.tool()
def capital_flow(market: int, code: str) -> dict:
    '''
    资金流向 - 基于成交数据分析主力资金动向
        Args:
            market: int - ''' + _MARKET_DESC + '''
            code: str   - 股票代码
        Returns:
            Dict: {
                "main_net_inflow": 12345678,  # 主力净流入（元）
                "super_large": 5678901,       # 特大单净流入
                "large": 6666777,             # 大单净流入
                "medium": -123456,            # 中单净流入
                "small": -234567,             # 小单净流入
                "main_ratio": 0.65,           # 主力占比
                "assessment": "主力流入"     # 评估结果
            }
    '''
    from tdx_mcp.tools.stock_analysis import capital_flow as _capital_flow
    return _capital_flow(hq(), MARKET(market), code)

@mcp.tool()
def hot_concepts(top_n: int = 10) -> dict:
    '''
    热门概念板块 - 基于涨幅和热度排序的概念板块分析
        Args:
            top_n: int - 返回前N个热门板块，默认10
        Returns:
            Dict: {
                "concepts": [
                    {"name": "DeepSeek概念", "code": "BK0888", "price": 1234.56, "change_pct": 5.23, "heat_score": 85},
                    ...
                ],
                "market_heat": "活跃"  # 市场整体热度
            }
    '''
    from tdx_mcp.tools.stock_analysis import hot_concepts as _hot_concepts
    return _hot_concepts(hq(), top_n)

# ============ 高级选股工具 ============

@mcp.tool()
def dragon_tiger(date: str = None) -> dict:
    '''
    龙虎榜数据 - 查看异动股票（涨停、跌停、大幅波动）
        Args:
            date: str - 日期（可选，格式YYYY-MM-DD，默认今日）
        Returns:
            Dict: {
                "stocks": [
                    {
                        "code": "000001",
                        "name": "平安银行",
                        "reason": "日涨幅偏离值达7%",
                        "value": 500000000
                    },
                    ...
                ],
                "total_count": 50,
                "date": "2026-04-04"
            }
    '''
    from tdx_mcp.tools.advanced_screener import dragon_tiger_list
    return dragon_tiger_list(hq(), date)

@mcp.tool()
def stock_screener(
    market: int = 6,
    price_min: float = None,
    price_max: float = None,
    change_pct_min: float = None,
    change_pct_max: float = None,
    volume_min: int = None,
    turnover_min: float = None,
    amount_min: int = None,
    sort_by: str = 'change_pct',
    limit: int = 50
) -> dict:
    '''
    智能选股器 - 多条件筛选股票
        Args:
            market: int - ''' + _CATEGORY_DESC + '''，默认6(A股)
            price_min: float - 最低价格
            price_max: float - 最高价格
            change_pct_min: float - 最低涨幅(%)
            change_pct_max: float - 最高涨幅(%)
            volume_min: int - 最小成交量
            turnover_min: float - 最小换手率(%)
            amount_min: int - 最小成交额
            sort_by: str - 排序字段(change_pct/volume/amount/turnover)
            limit: int - 返回数量，默认50
        Returns:
            Dict: {
                "stocks": [
                    {
                        "code": "000001",
                        "name": "平安银行",
                        "price": 12.35,
                        "change_pct": 2.5,
                        "volume": 12345678,
                        "amount": 152345678,
                        "turnover": 3.5
                    },
                    ...
                ],
                "filtered_count": 100,
                "total_count": 3000
            }
    '''
    from tdx_mcp.tools.advanced_screener import stock_screener as _stock_screener
    
    # 构建筛选条件
    filters = {}
    if price_min is not None:
        filters['price_min'] = price_min
    if price_max is not None:
        filters['price_max'] = price_max
    if change_pct_min is not None:
        filters['change_pct_min'] = change_pct_min
    if change_pct_max is not None:
        filters['change_pct_max'] = change_pct_max
    if volume_min is not None:
        filters['volume_min'] = volume_min
    if turnover_min is not None:
        filters['turnover_min'] = turnover_min
    if amount_min is not None:
        filters['amount_min'] = amount_min
    
    return _stock_screener(hq(), market, filters, sort_by, limit)

@mcp.tool()
def top_gainers(limit: int = 20) -> dict:
    '''
    涨幅榜 - 涨幅最大的股票
        Args:
            limit: int - 返回数量，默认20
        Returns:
            Dict: {
                "stocks": [
                    {"code": "000001", "name": "平安银行", "price": 12.35, "change_pct": 10.0},
                    ...
                ],
                "count": 20
            }
    '''
    from tdx_mcp.tools.advanced_screener import top_gainers as _top_gainers
    return _top_gainers(hq(), limit)

@mcp.tool()
def top_losers(limit: int = 20) -> dict:
    '''
    跌幅榜 - 跌幅最大的股票
        Args:
            limit: int - 返回数量，默认20
        Returns:
            Dict: {
                "stocks": [
                    {"code": "000001", "name": "平安银行", "price": 12.35, "change_pct": -10.0},
                    ...
                ],
                "count": 20
            }
    '''
    from tdx_mcp.tools.advanced_screener import top_losers as _top_losers
    return _top_losers(hq(), limit)

@mcp.tool()
def high_turnover(limit: int = 20) -> dict:
    '''
    高换手率股票 - 换手率最高的股票
        Args:
            limit: int - 返回数量，默认20
        Returns:
            Dict: {
                "stocks": [
                    {"code": "000001", "name": "平安银行", "price": 12.35, "turnover_rate": 15.5},
                    ...
                ],
                "count": 20
            }
    '''
    from tdx_mcp.tools.advanced_screener import high_turnover as _high_turnover
    return _high_turnover(hq(), limit)


def main():
    """MCP Server 入口点"""
    mcp.run()

if __name__ == '__main__':
    main()
