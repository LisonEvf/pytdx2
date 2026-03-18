from client.quotationClient import QuotationClient
from mcp.server.fastmcp import FastMCP

from const import CATEGORY, MARKET, PERIOD

mcp = FastMCP('TDX MCP Server')

quotationClient = QuotationClient(True, True)
quotationClient.connect().login()

@mcp.tool()
def get_Index_Overview():
    ''' 获取指数概况
    :return: 上证、深证、北证、创业、科创、沪深指数数据的JSON字符串
    '''
    return quotationClient.get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001'), (MARKET.SZ, '399006'), (MARKET.BJ, '899050'), (MARKET.SH, '000688'), (MARKET.SH, '000300')])

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
    return quotationClient.get_quotes(code_list, code)

@mcp.tool()
def stock_kline(market: MARKET, code: str, period: PERIOD, start = 0, count = 800, times: int = 1):
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
    return quotationClient.get_kline(market, code, period, start, count, times)


@mcp.tool()
def stock_top_board(category: CATEGORY = CATEGORY.A):
    '''
    获取股票排行榜
    Args:
        category: CATEGORY
            SH: 上证A股
            SZ: 深证A股
            A: 沪深A股
            B: 沪深B股
            BJ: 北证A股
            CYB: 创业板
            KCB: 科创板
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
    return quotationClient.get_stock_top_board(category)

@mcp.tool()
def get_top_stock(category: CATEGORY = CATEGORY.A) -> str:
    '''
    获取板块内的股票列表
    Args:
        category: 板块分类
            SH: 上证A股
            SZ: 深证A股
            A: 沪深A股
            B: 沪深B股
            BJ: 北证A股
            CYB: 创业板
            KCB: 科创板
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
    return quotationClient.get_stock_quotes_list(category)

@mcp.tool()
def get_company_info(market: MARKET, code: str) -> str:
    '''
    获取公司信息
    Args:
        market: MARKET  # 市场类型
        code: str(code) # 股票代码
    Returns:
        {
            'name': str(name),
            'content': str(content),
        }
    '''
    return quotationClient.get_company_info(market, code)

if __name__ == '__main__':
    mcp.run()