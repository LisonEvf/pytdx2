from datetime import date
import zlib
from client.exQuotationClient import exQuotationClient
from client.quotationClient import QuotationClient
from const import (
    EX_CATEGORY,
    FILTER_TYPE,
    PERIOD,
    MARKET,
    BLOCK_FILE_TYPE,
    CATEGORY,
    SORT_TYPE,
)
import pandas as pd
from parser.ex_quotation import file, goods
from parser.quotation import server, stock

from utils.log import log
from client.boardClient import BoardClient, ExBoardClient
from const import (
    BLOCK_FILE_TYPE,
    CATEGORY,
    PERIOD,
    MARKET,
    EX_BOARD_TYPE,
    BOARD_TYPE,
)

if __name__ == "__main__":
    client = BoardClient()
    # # 117.34.114.31
    if client.connect().login(show_info=True):
        rs = client.get_board_count(market=BOARD_TYPE.ALL)
        print(f"{BOARD_TYPE.ALL} count : {rs['total']}")
        rs = client.get_board_list(market=BOARD_TYPE.ALL)
        df = pd.DataFrame(rs)
        print(f"{BOARD_TYPE.ALL} query total : {len(rs)}")
        for symbol in ["000070", "399372", "899050", "880686"]:
            members = client.get_board_members_quotes(board_symbol=symbol)
            print(f"{symbol} 板块成员数量 : {len(members)}")

    client = ExBoardClient()
    # # 117.34.114.31
    if client.connect().login(show_info=True):
        rs = client.get_board_count(market=EX_BOARD_TYPE.HK_ALL)
        print(f"{EX_BOARD_TYPE.HK_ALL} count : {rs['total']}")
        rs = client.get_board_list(market=EX_BOARD_TYPE.HK_ALL)
        df = pd.DataFrame(rs)
        print(f"{EX_BOARD_TYPE.HK_ALL} query total : {len(rs)}")

        for symbol in ["HK0285", "US0476"]:
            members = client.get_board_members_quotes(board_symbol=symbol)
            print(f"{symbol} 板块成员数量 : {len(members)}")
