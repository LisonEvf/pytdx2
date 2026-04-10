from typing import Union

from .baseStockClient import BaseStockClient, update_last_ack_time
from const import ADJUST, BOARD_TYPE, MARKET, PERIOD, EX_BOARD_TYPE, mac_hosts, mac_ex_hosts
from parser.mac_quotation import BoardCount, BoardList, BoardMembers, BoardMembersQuotes, SymbolBar, SymbolBelongBoard
from utils.log import log

class macQuotationClient(BaseStockClient):

    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = mac_hosts

    @update_last_ack_time
    def get_board_count(self, market: Union[BOARD_TYPE, EX_BOARD_TYPE]):
        return self.call(BoardCount(market))

    @update_last_ack_time
    def get_board_list(self, market: Union[BOARD_TYPE, EX_BOARD_TYPE], count=10000):
        MAX_LIST_COUNT = 150
        security_list = []
        page_size = min(count, MAX_LIST_COUNT)
        
        msg = f"TDX 板块列表：{market} 查询总量{count}"
        log.debug(msg)
        
        for start in range(0, count, page_size):
            current_count = min(page_size, count - start)
            part = self.call(BoardList(board_type=market, start=start, page_size=current_count))
            
            if len(part) > 0:
                security_list.extend(part)
            
            if len(part) < current_count:
                log.debug(f"{msg} 数据量不足，获取结束")
                break
                
        return security_list

    @update_last_ack_time
    def get_board_members_quotes(self, board_symbol: str, count=10000):
        MAX_LIST_COUNT = 80
        security_list = []
        
        msg = f"TDX 板块成分报价：{board_symbol} 查询总量{count}"
        log.debug(msg)
        
        for start in range(0, count, MAX_LIST_COUNT):
            current_count = min(MAX_LIST_COUNT, count - start)
            rs = self.call(BoardMembersQuotes(board_symbol=board_symbol, start=start, page_size=current_count))
            part = rs["stocks"]
            
            if len(part) > 0:
                security_list.extend(part)
            
            if len(part) < current_count:
                log.debug(f"{msg} 数据量不足，获取结束")
                break
                
        return security_list

    # @update_last_ack_time
    def get_board_members(self, board_symbol: str, count=10000):
        MAX_LIST_COUNT = 80
        security_list = []
        
        msg = f"TDX 板块成员：{board_symbol} 查询总量{count}"
        log.debug(msg)
        
        for start in range(0, count, MAX_LIST_COUNT):
            current_count = min(MAX_LIST_COUNT, count - start)
            rs = self.call(BoardMembers(board_symbol=board_symbol, start=start, page_size=current_count))
            part = rs["stocks"]
            
            if len(part) > 0:
                security_list.extend(part)
            
            if len(part) < current_count:
                log.debug(f"{msg} 数据量不足，获取结束")
                break
                
        return security_list

    # @update_last_ack_time
    def get_symbol_belong_board(self, symbol: str, market: MARKET) -> list[dict]:
        parser = SymbolBelongBoard(symbol=symbol, market=market)
        df = self.call(parser)
        return df

    @update_last_ack_time
    def get_symbol_bars(
        self, market: MARKET, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800, fq: ADJUST = ADJUST.NONE
    ) -> list[dict]:
        MAX_LIST_COUNT = 700
        page_size = min(count, MAX_LIST_COUNT)
        security_list = []
        start = 0

        msg = f"TDX bar :{market} {code} {period} 查询总量{count} {start}  "
        log.debug(msg)

        for start in range(0, count, page_size):
            # 计算本次请求的实际数量，最后一次根据剩余数据减少
            current_count = min(page_size, count - start)

            parser = SymbolBar(market=market, code=code, period=period, times=times, start=start, count=current_count, fq=fq)
            part = self.call(parser)

            if len(part) > 0:
                security_list.extend(part)

            if len(part) < current_count:
                log.debug(f"{msg} 数据量不足,获取结束")
                break

        return security_list
    
class macExQuotationClient(macQuotationClient):
    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = mac_ex_hosts