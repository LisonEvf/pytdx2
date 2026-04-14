from typing import Union

from .baseStockClient import BaseStockClient, update_last_ack_time, _paginate
from opentdx.const import ADJUST, BOARD_TYPE, MARKET, PERIOD, EX_BOARD_TYPE, mac_hosts, mac_ex_hosts
from opentdx.parser.mac_quotation import (
    BoardCount, BoardList, BoardMembers, BoardMembersQuotes,
    SymbolBar, SymbolBelongBoard,
    ServerInit, FileList, FileDownload,
    StockQuery, BatchStockData,
    StockDetail, StockBarCount, StockSmallInfo, KlineOffset,
)

class macQuotationClient(BaseStockClient):

    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False, hosts=None):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = hosts or mac_hosts

    @update_last_ack_time
    def get_board_count(self, market: Union[BOARD_TYPE, EX_BOARD_TYPE]):
        return self.call(BoardCount(market))

    @update_last_ack_time
    def get_board_list(self, market: Union[BOARD_TYPE, EX_BOARD_TYPE], count=10000):
        return _paginate(
            lambda s, c: self.call(BoardList(board_type=market, start=s, page_size=c)),
            150, count,
        )

    @update_last_ack_time
    def get_board_members_quotes(self, board_symbol: str, count=10000):
        return _paginate(
            lambda s, c: self.call(BoardMembersQuotes(board_symbol=board_symbol, start=s, page_size=c))["stocks"],
            80, count,
        )

    @update_last_ack_time
    def get_board_members(self, board_symbol: str, count=10000):
        return _paginate(
            lambda s, c: self.call(BoardMembers(board_symbol=board_symbol, start=s, page_size=c))["stocks"],
            80, count,
        )

    @update_last_ack_time
    def get_symbol_belong_board(self, symbol: str, market: MARKET) -> list[dict]:
        return self.call(SymbolBelongBoard(symbol=symbol, market=market))

    @update_last_ack_time
    def get_symbol_bars(
        self, market: MARKET, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800, adjust: ADJUST = ADJUST.NONE
    ) -> list[dict]:
        return _paginate(
            lambda s, c: self.call(SymbolBar(market=market, code=code, period=period, times=times, start=s, count=c, fq=adjust)),
            700, count, start,
        )

    @update_last_ack_time
    def server_init(self) -> bool:
        """服务器初始化/订阅，返回是否成功"""
        return self.call(ServerInit())

    @update_last_ack_time
    def get_file_list(self, filename: str, offset: int = 0) -> dict:
        """查询文件列表信息，返回 offset/size/hash"""
        return self.call(FileList(filename=filename, offset=offset))

    @update_last_ack_time
    def download_file(self, filename: str, index: int = 1, offset: int = 0, size: int = 30000) -> dict:
        """下载文件内容，返回 index/size/content"""
        return self.call(FileDownload(filename=filename, index=index, offset=offset, size=size))

    @update_last_ack_time
    def get_stock_query(self, market: MARKET, code: str, flag: int = 1, unk: int = 0) -> dict:
        """查询股票行情信息"""
        return self.call(StockQuery(market=market, code=code, flag=flag, unk=unk))

    @update_last_ack_time
    def get_batch_stock_data(self, market: MARKET, code: str) -> dict:
        """获取批量股票数据（OHLCV 等）"""
        return self.call(BatchStockData(market=market, code=code))

    @update_last_ack_time
    def get_stock_detail(self, market: MARKET, code: str) -> list:
        """获取股票分笔明细（tick 数据）"""
        return self.call(StockDetail(market=market, code=code))

    @update_last_ack_time
    def get_stock_bar_count(self, market: MARKET, code: str, count: int = 500) -> list:
        """获取股票K线柱数据"""
        return self.call(StockBarCount(market=market, code=code, count=count))

    @update_last_ack_time
    def get_stock_small_info(self, market: MARKET, code: str, period: int = 5, flag: int = 1) -> list:
        """获取股票分钟级数据"""
        return self.call(StockSmallInfo(market=market, code=code, period=period, flag=flag))

    @update_last_ack_time
    def get_kline_offset(self, offset: int = 0, count: int = 128000) -> list:
        """获取K线偏移表（股票/指数列表）"""
        return self.call(KlineOffset(offset=offset, count=count))
