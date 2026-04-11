from opentdx.parser.quotation.auction import Auction
from opentdx.parser.quotation.chart_sampling import ChartSampling
from opentdx.parser.quotation.count import Count
from opentdx.parser.quotation.history_orders import HistoryOrders
from opentdx.parser.quotation.history_tick_chart import HistoryTickChart
from opentdx.parser.quotation.history_transaction_with_trans import HistoryTransactionWithTrans
from opentdx.parser.quotation.history_transaction import HistoryTransaction
from opentdx.parser.quotation.index_info import IndexInfo
from opentdx.parser.quotation.index_momentum import IndexMomentum
from opentdx.parser.quotation.kline_offset import K_Line_Offset
from opentdx.parser.quotation.kline import K_Line
from opentdx.parser.quotation.list import List
from opentdx.parser.quotation.list2 import List2
from opentdx.parser.quotation.quotes_detail import QuotesDetail
from opentdx.parser.quotation.quotes_encrypt import QuotesEncrypt
from opentdx.parser.quotation.quotes_list import QuotesList
from opentdx.parser.quotation.quotes import Quotes
from opentdx.parser.quotation.tick_chart import TickChart
from opentdx.parser.quotation.top_board import TopBoard
from opentdx.parser.quotation.transaction import Transaction
from opentdx.parser.quotation.unusual import Unusual
from opentdx.parser.quotation.volume_profile import VolumeProfile

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

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser
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