from datetime import date

import pandas as pd
# from opentdx.client import macQuotationClient as QuotationClient, macExQuotationClient as exQuotationClient
from opentdx.client import macQuotationClient , QuotationClient , macExQuotationClient
from opentdx.const import ADJUST, BLOCK_FILE_TYPE, CATEGORY, EX_CATEGORY, EX_MARKET, FILTER_TYPE, MARKET, PERIOD, EX_BOARD_TYPE, BOARD_TYPE, SORT_TYPE
from opentdx.const import mac_hosts,    mac_ex_hosts
from opentdx.parser.ex_quotation import file, goods
from opentdx.parser.quotation import server, stock

if __name__ == "__main__":
        
    test_symbol_bars = True
    test_board = True
    
    # df = tdxService.get_tdx_board_members(symbol="HK0273",count=3)
    # print(df)
    
    category = CATEGORY.CYB
    client = macQuotationClient()
    client.hosts = mac_hosts
    client.connect().login()

    for i in range(30,100):
        rs = client.count_board_members(board_symbol=str(i),count=1)
        if rs and rs['total']>0:
            print(i, rs['total'], rs['stocks'])

    exit()
    
    ex_client = macExQuotationClient()
    ex_client.hosts = mac_ex_hosts
    ex_client.connect().login()
    # rs = client.get_stock_quotes_list(category=category,count=10,sortType=SORT_TYPE.CHANGE_PCT)
    # df1 = pd.DataFrame(rs)
    # print(df1.iloc[3])
    
    
    board_symbol = str(EX_CATEGORY.US.value)

    rs = ex_client.get_board_members(board_symbol=EX_CATEGORY.USZGG,count=100)
    df = pd.DataFrame(rs)
    print(df)
    

    for item in EX_MARKET:
        rs = ex_client.count_board_members(board_symbol=str(item.value),count=1)
        if len(rs)>0:

            print(rs, rs['total'], rs['stocks'])
            



    # print(df.iloc[1])
    
    # macClient = macExQuotationClient()
    # macClient.hosts = ex_mixin_hosts
    # # MARKET.SH	880761	锂矿
    # macClient.connect()
    # board_symbol = str(CATEGORY.CYB.value)
    # board_symbol = "HK0273"
    # rs = macClient.get_board_members_quotes(board_symbol=board_symbol,count=4)
    # df = pd.DataFrame(rs)
    # # df = df[['symbol','ex_price']]
    # print(df)
    # # print(df.iloc[1])
    exit()
    
    exit()