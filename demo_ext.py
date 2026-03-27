from datetime import date

import pandas as pd
from tdx_mcp.client import QuotationClient, exQuotationClient
from tdx_mcp.const import ADJUST, BLOCK_FILE_TYPE, CATEGORY, EX_CATEGORY, FILTER_TYPE, MARKET, PERIOD, SORT_TYPE
from tdx_mcp.parser.ex_quotation import file, goods
from tdx_mcp.parser.quotation import server, stock

if __name__ == "__main__":
    client = QuotationClient()
    if client.connect().login():
        print("无复权")
        print(pd.DataFrame(client.get_kline(MARKET.SZ, "000100", PERIOD.DAILY, count=3)))
        print("无复权")
        print(pd.DataFrame(client.get_kline(MARKET.SZ, "000100", PERIOD.DAILY, count=3, fq=ADJUST.QFQ)))
        print("后复权")
        print(pd.DataFrame(client.get_kline(MARKET.SZ, "000100", PERIOD.DAILY, count=3, fq=ADJUST.HFQ)))
        # part = client.call(stock.K_Line(MARKET.SZ, "000001", PERIOD.DAILY))
