from client.quotationClient import QuotationClient
from mcp.server.fastmcp import FastMCP

from const import CATEGORY, MARKET, PERIOD

mcp = FastMCP('TDX MCP Server')

quotationClient = QuotationClient()
quotationClient.connect().login()

@mcp.tool()
def get_Index_Overview():
    ''' 获取指数概况
    :return: 上证、深证、北证、创业、科创、沪深指数数据的JSON字符串
    '''
    return quotationClient.get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001'), (MARKET.SZ, '399006'), (MARKET.BJ, '899050'), (MARKET.SH, '000688'), (MARKET.SH, '000300')])

@mcp.tool()
def get_security_quotes( all_stock, code=None) -> str:
    '''
    获取简略行情
    支持三种形式的参数
    get_security_quotes(market, code )
    get_security_quotes((market, code))
    get_security_quotes([(market1, code1), (market2, code2)] )

    Args:
        market: 市场类型，必填项
        code: 股票代码，必填项
    :return: 简略行情的JSON字符串
    '''
    if code is not None:
        all_stock = [(all_stock, code)]
    elif (isinstance(all_stock, list) or isinstance(all_stock, tuple))\
            and len(all_stock) == 2 and type(all_stock[0]) is int:
        all_stock = [all_stock]
    return quotationClient.get_security_quotes(all_stock)

@mcp.tool()
def get_KLine_data(market: MARKET, code: str, period: PERIOD = PERIOD.DAY, start: int = 0, count: int = 800) -> str:
    '''
    获取K线数据
    Args:
        market: 市场类型，必填项
        code: 股票代码，必填项
        period: K线周期，默认为日线
        start: 起始位置，默认为0
        count: 获取数量，默认为800
    
    Returns:
         K线数据的JSON字符串
    '''
    return quotationClient.get_KLine_data(market, code, period, start, count)


@mcp.tool()
def get_top_board(category: CATEGORY = CATEGORY.A) -> str:
    '''
    获取行情全景
    Args:
        category: 板块分类
            SH: 上证A股
            SZ: 深证A股
            A: 沪深A股
            B: 沪深B股
            BJ: 北证A股
            CYB: 创业板
            KCB: 科创板
    Returns:
         行情全景的JSON字符串
    '''
    return quotationClient.get_top_stock_board(category)

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
    Returns:
        板块内的股票列表的JSON字符串
    '''
    return quotationClient.get_security_quotes_by_category(category)

@mcp.tool()
def get_company_info(market: MARKET, code: str) -> str:
    '''
    获取公司信息
    Args:
        market: 市场类型，必填项
        code: 股票代码，必填项
    Returns:
        公司信息的JSON字符串
    '''
    return quotationClient.get_company_info(market, code)

if __name__ == '__main__':
    mcp.run()