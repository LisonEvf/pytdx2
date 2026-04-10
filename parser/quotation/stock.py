from parser.quotation.auction import Auction
from parser.quotation.chart_sampling import ChartSampling
from parser.quotation.count import Count
from parser.quotation.history_orders import HistoryOrders
from parser.quotation.history_tick_chart import HistoryTickChart
from parser.quotation.history_transaction_with_trans import HistoryTransactionWithTrans
from parser.quotation.history_transaction import HistoryTransaction
from parser.quotation.index_info import IndexInfo
from parser.quotation.index_momentum import IndexMomentum
from parser.quotation.kline_offset import K_Line_Offset
from parser.quotation.kline import K_Line
from parser.quotation.list import List
from parser.quotation.list2 import List2
from parser.quotation.quotes_detail import QuotesDetail
from parser.quotation.quotes_encrypt import QuotesEncrypt
from parser.quotation.quotes_list import QuotesList
from parser.quotation.quotes import Quotes
from parser.quotation.tick_chart import TickChart
from parser.quotation.top_board import TopBoard
from parser.quotation.transaction import Transaction
from parser.quotation.unusual import Unusual
from parser.quotation.volume_profile import VolumeProfile

__all__ = [
    'Auction',
    'ChartSampling',
    'Count',
    'HistoryOrders',
    'HistoryTickChart',
    'HistoryTransactionWithTrans',
    'HistoryTransaction',
    'IndexInfo',
    'IndexMomentum',
    'K_Line_Offset',
    'K_Line',
    'List',
    'List2',
    'QuotesDetail',
    'QuotesEncrypt',
    'QuotesList',
    'Quotes',
    'TickChart',
    'TopBoard',
    'Transaction',
    'Unusual',
    'VolumeProfile',
]

from const import MARKET
from parser.baseParser import BaseParser, register_parser
import struct
from typing import override


    
@register_parser(0x452)
class f452(BaseParser):
    def __init__(self, start:int = 0, count:int = 2000):
        self.body = struct.pack('<IIIH', start, count, 1, 0)

    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])
        result = []
        for i in range(count):
            market, code_num, p1, p2 = struct.unpack('<BIff', data[i * 13 + 2: i * 13 + 15])
            result.append({
                'market': MARKET(market),
                'code': f'{code_num}',
                'p1': p1,
                'p2': p2
            })

        return result