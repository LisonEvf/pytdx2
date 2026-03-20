from client.baseStockClient import update_last_ack_time
from const import (
    board_hosts,
    ex_board_hosts,
    BOARD_TYPE,
    EX_BOARD_TYPE,
)
from typing import Union


from client.exQuotationClient import exQuotationClient
from client.quotationClient import QuotationClient

from parser import board_quotation


class BoardClientMixin:
    @update_last_ack_time
    def get_board_count(self, market: Union[BOARD_TYPE, EX_BOARD_TYPE]):
        return self.call(board_quotation.BoardCount(market))

    @update_last_ack_time
    def get_board_list(self, market: Union[BOARD_TYPE, EX_BOARD_TYPE], count=10000):
        MAX_LIST_COUNT = 150
        security_list = []
        page_size = min(count, MAX_LIST_COUNT)
        start = 0
        while count > 0:
            part = self.call(
                board_quotation.BoardList(
                    board_type=market, start=start, page_size=page_size
                )
            )
            if len(part) > 0:
                security_list.extend(part)
            if len(part) < min(count, MAX_LIST_COUNT):
                break
            count -= len(part)
            start += len(part)
        return security_list

    # @update_last_ack_time
    def get_board_members_quotes(self, board_symbol: str, count=10000):
        MAX_LIST_COUNT = 80
        security_list = []
        page_size = min(count, MAX_LIST_COUNT)
        start = 0
        while count > 0:
            rs = self.call(
                board_quotation.BoardMembersQuotes(
                    board_symbol=board_symbol, start=start, page_size=page_size
                )
            )
            part = rs["stocks"]
            if len(part) > 0:
                security_list.extend(part)
            if len(part) < min(count, MAX_LIST_COUNT):
                break
            count -= len(part)
            start += len(part)
        return security_list

    @update_last_ack_time
    def get_board_members(self, board_symbol: str, count=10000):
        MAX_LIST_COUNT = 80
        security_list = []
        page_size = min(count, MAX_LIST_COUNT)
        start = 0
        while count > 0:
            rs = self.call(
                board_quotation.BoardMembers(
                    board_symbol=board_symbol, start=start, page_size=page_size
                )
            )
            part = rs["stocks"]
            if len(part) > 0:
                security_list.extend(part)
            if len(part) < min(count, MAX_LIST_COUNT):
                break
            count -= len(part)
            start += len(part)
        return security_list


# ---------------------- 双继承实现 ----------------------
class ExBoardClient(BoardClientMixin, exQuotationClient):
    def __init__(
        self,
        multithread=False,
        heartbeat=False,
        auto_retry=False,
        raise_exception=False,
    ):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = ex_board_hosts

    """继承Mixin + 专属父类exQuotationClient"""
    # 无需再写任何重复代码！所有逻辑都在Mixin中
    pass


class BoardClient(BoardClientMixin, QuotationClient):
    def __init__(
        self,
        multithread=False,
        heartbeat=False,
        auto_retry=False,
        raise_exception=False,
    ):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = board_hosts

    """继承Mixin + 专属父类QuotationClient"""
    # 无需再写任何重复代码！
    pass
