from datetime import date

import pandas as pd
from tdx_mcp.client import QuotationClient, exQuotationClient
from tdx_mcp.const import ADJUST, BLOCK_FILE_TYPE, CATEGORY, EX_CATEGORY, FILTER_TYPE, MARKET, PERIOD, EX_BOARD_TYPE, BOARD_TYPE
from tdx_mcp.const import mixin_hosts, ex_mixin_hosts
from tdx_mcp.parser.ex_quotation import file, goods
from tdx_mcp.parser.quotation import server, stock


if __name__ == "__main__":
        
    test_symbol_bars = True
    test_board = True
    
    client = QuotationClient()
    client.hosts = mixin_hosts
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
        
        board_symbol = "HK0281"
        rs = exClient.get_board_members(board_symbol=board_symbol)
        df = pd.DataFrame(rs)
        print(f"港股板块 {board_symbol} 成员数量: {len(df)} 展示部分:")
        print(df[:3])
        
        board_symbol = "US0218"
        rs = exClient.get_board_members(board_symbol=board_symbol)
        df = pd.DataFrame(rs)
        print(f"美股板块 {board_symbol} 成员数量: {len(df)} 展示部分:")
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


