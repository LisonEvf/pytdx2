from datetime import date

import pandas as pd
# from opentdx.client import macQuotationClient as QuotationClient, macExQuotationClient as exQuotationClient
from opentdx.client import exQuotationClient , QuotationClient 
from opentdx.const import ADJUST, BLOCK_FILE_TYPE, CATEGORY, EX_CATEGORY, FILTER_TYPE, MARKET, PERIOD, EX_BOARD_TYPE, BOARD_TYPE, SORT_TYPE
from opentdx.const import mac_hosts , mac_ex_hosts
from opentdx.parser.ex_quotation import file, goods
from opentdx.parser.quotation import server, stock


if __name__ == "__main__":
        
    test_symbol_bars = True
    test_board = True
    
    
    category = CATEGORY.FXJS
    board_symbol = str(CATEGORY.FXJS.value)
    client = QuotationClient()
    client.hosts = mac_hosts
    client.connect().login()
    print("测试sp模式")
    try:
        rs = client.get_board_members_quotes(board_symbol=board_symbol,count=10)
    except Exception as e:
        print("启用sp模式,使用支持通用接口的ip")
        print(e)
        
        
    print("使用get_stock_quotes_list查询板块股票")
    client.sp().connect().login()
    rs = client.get_stock_quotes_list(category=category,count=10,sortType=SORT_TYPE.CHANGE_PCT)
    df = pd.DataFrame(rs)
    print(df)
    
    
    print("启用get_board_members_quotes查询板块股票")
    rs = client.get_board_members_quotes(board_symbol=category,count=10)
    df = pd.DataFrame(rs)
    print(df)
            
    print("支持自定义字段 ohlc , 增加ah_code , 查询881394板块")
    ah_code_filter = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 0x4a)
    rs = client.get_board_members_quotes(board_symbol="881394",count=10, filter=ah_code_filter)
    df = pd.DataFrame(rs)
    print(df[[ 'name', 'open', 'high', 'low', 'close', 'vol',  'ah_code']])

    
    print("支持自定义字段 ohlc")
    filter = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4)
    rs = client.get_board_members_quotes(board_symbol=board_symbol,count=10, filter=filter)
    df = pd.DataFrame(rs)
    print(df)
    
    exClient = exQuotationClient()
    exClient.sp().connect().login()
    

    print("支持自定义字段 ohlc , 增加ah_code , [HK0266] 反向查询A股代码")
    ah_code_filter = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 0x4a)
    rs = exClient.get_board_members_quotes(board_symbol="HK0266",count=10, filter=ah_code_filter)
    df = pd.DataFrame(rs)
    print(df[[ 'name', 'open', 'high', 'low', 'close', 'vol',  'ah_code']])
    
    
    board_symbol = "HK0281"
    rs = exClient.get_board_members_quotes(board_symbol=board_symbol)
    df = pd.DataFrame(rs)
    print(f"港股板块 {board_symbol} 成员数量: {len(df)} 展示部分:")
    print(df[:3])
    
    board_symbol = "US0218"
    rs = exClient.get_board_members_quotes(board_symbol=board_symbol)
    df = pd.DataFrame(rs)
    print(f"美股板块 {board_symbol} 成员数量: {len(df)} 展示部分:")
    print(df[:3])
    
    print("查询香港主板")
    board_symbol = EX_CATEGORY.HSI
    rs = exClient.get_board_members_quotes(board_symbol=board_symbol,count=10, filter=filter)
    df = pd.DataFrame(rs)
    print(f"查询香港主板 {board_symbol} 成员数量: {len(df)} 展示部分:")
    print(df[:3])
    exit()

    count = 40
    symbol = '600900'
    market = MARKET.SH
    fq=ADJUST.QFQ
    rs = client.get_symbol_bars(market, symbol, PERIOD.DAILY, count=count, fq=fq)
    df = pd.DataFrame(rs)
    df['换手'] = df['vol'] / (df['float_shares'] * 10000) * 100
    df['换手'] = df['换手'].round(2).abs()
    print(f"股票 {market} {symbol} {fq} 的前{count}个交易日行情数据如下:")
    print(df)
    exit()
    
    exClient = exQuotationClient()
    exClient.hosts = ex_mixin_hosts
    exClient.connect().login()

    board_symbol = "US0401"
    rs = exClient.get_board_members_quotes(board_symbol=board_symbol,count=2)
    print(rs)

    
    exit()
    
    if client.connect().login():
        symbol = '000100'
        market = MARKET.SZ
    
        print("无复权   ", symbol, market)
        print(pd.DataFrame(client.get_kline(market, symbol, PERIOD.DAILY, count=3)))
        print("前复权   ", symbol, market)
        print(pd.DataFrame(client.get_kline(market, symbol, PERIOD.DAILY, count=4, adjust=ADJUST.QFQ)))
        print("后复权   ", symbol, market)
        print(pd.DataFrame(client.get_kline(market, symbol, PERIOD.DAILY, count=3, adjust=ADJUST.HFQ)))
        # part = client.call(stock.K_Line(MARKET.SZ, "000001", PERIOD.DAILY))
        

    client = QuotationClient()
    client.hosts = mixin_hosts
    client.connect().login()

        
    exClient = exQuotationClient()
    exClient.hosts = ex_mixin_hosts
    exClient.connect().login()

    if test_board:
        print("板块列表查询 ")
        market=BOARD_TYPE.DQ
        rs = client.get_board_list(market=market)
        df = pd.DataFrame(rs)
        print(f"地区板块 {market} 查询板块列表: {len(df)} 展示部分:")
        print(df[:3])
        
        market=BOARD_TYPE.HY
        rs = client.get_board_list(market=market)
        df = pd.DataFrame(rs)
        print(f"行业板块 {market} 查询板块列表: {len(df)} 展示部分:")
        print(df[:3])
        
        market=EX_BOARD_TYPE.HK_ALL
        rs = exClient.get_board_list(market=market)
        df = pd.DataFrame(rs)
        print(f"港股板块 {market} 查询板块列表: {len(df)} 展示部分:")
        print(df[:3])
        
        market=EX_BOARD_TYPE.US_ALL
        rs = exClient.get_board_list(market=market)
        df = pd.DataFrame(rs)
        print(f"美股板块 {market} 查询板块列表: {len(df)} 展示部分:")
        print(df[:3])
        
        print("板块测试 [client.get_board_members] 仅查询关系 ")
        
        # MARKET.SH	880761	锂矿
        board_symbol = "880761"
        rs = client.get_board_members(board_symbol=board_symbol)
        df = pd.DataFrame(rs)
        print(f"板块测试 {board_symbol} 成员数量: {len(df)} 展示部分:")
        print(df[:3])
        
        # 重点指数  MARKET.SH 000683	
        board_symbol = "000683"
        rs = client.get_board_members(board_symbol=board_symbol)
        df = pd.DataFrame(rs)
        print(f"重点指数 {board_symbol} 成员数量: {len(df)} 展示部分:")
        print(df[:3])
        
        
        print("***** 板块测试结束 *****")
            
        symbol = '000100'
        market = MARKET.SZ
        df = client.get_symbol_belong_board(symbol=symbol, market=market)
        print(f"股票 {market} {symbol} 所属板块: {len(df)} 展示部分:")
        print(df[:3])
                
                
        # symbol = '00700'
        # market = EX_CATEGORY.HK_MAIN_BOARD
        # df = exClient.get_symbol_belong_board(symbol=symbol, market=market)
        # print(f"港股 {market} {symbol} 所属板块 返回结果与股票不太一致,未解析")
        # print(df[:3])
                
        
        # symbol = 'TSLA'
        # market = EX_CATEGORY.US_STOCK
        # df = exClient.get_symbol_belong_board(symbol=symbol, market=market)
        # print(f"美股 {market} {symbol} 所属板块 返回结果与股票不太一致,未解析")
        # print(df[:3])
    
    

    if test_symbol_bars :
        
        count = 3
        print("get_symbol_bars 测试 股票、指数、港股、美股、板块、期货, 理论上所有code均支持, 需特定ip才能使用")
        
        # 股票
        symbol = '000100'
        market = MARKET.SZ
        fq=ADJUST.HFQ
        rs = client.get_symbol_bars(market, symbol, PERIOD.DAILY, count=count, fq=fq)
        df = pd.DataFrame(rs)
        print(f"股票 {market} {symbol} {fq} 的前{count}个交易日行情数据如下:")
        print(df)
        
        # 指数
        symbol = '880310'
        market = MARKET.SH
        fq=ADJUST.QFQ
        rs = client.get_symbol_bars(market, symbol, PERIOD.DAILY, count=count, fq=fq)
        df = pd.DataFrame(rs)
        print(f"指数 {market} {symbol} {fq} 的前{count}个交易日行情数据如下:")
        print(df)
        
        
        print("港股 美股 切换到 exClient, 出入参相同, float_shares为流通股,可以自行计算换手率")
        
        symbol = '00100'
        market = EX_CATEGORY.HK_MAIN_BOARD
        rs = exClient.get_symbol_bars(market, symbol, PERIOD.DAILY, count=count)
        df = pd.DataFrame(rs)
        print(f"港股 {market} {symbol} 的前{count}个交易日行情数据如下:")
        print(df)
        
        
        symbol = 'TSLA'
        market = EX_CATEGORY.US_STOCK
        rs = exClient.get_symbol_bars(market, symbol, PERIOD.WEEKLY, count=count)
        df = pd.DataFrame(rs)
        print(f"美股 {market} {symbol} 的前{count}个交易日行情数据如下:")
        print(df)

        symbol = 'HK0281'
        market = EX_CATEGORY.EXTENDED_SECTOR_INDEX
        rs = exClient.get_symbol_bars(market, symbol, PERIOD.WEEKLY, count=count)
        df = pd.DataFrame(rs)
        print(f"港股板块 {market} {symbol} 的前{count}个交易日行情数据如下:")
        print(df)
        
        
        symbol = 'US0218'
        market = EX_CATEGORY.EXTENDED_SECTOR_INDEX
        rs = exClient.get_symbol_bars(market, symbol, PERIOD.DAILY, count=count)
        df = pd.DataFrame(rs)
        print(f"美股板块 {market} {symbol} 的前10个交易日行情数据如下:")
        print(df)
        
    
    
    client.disconnect()
    exClient.disconnect()