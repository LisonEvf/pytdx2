from parser.quotation.auction import Auction
from parser.quotation.board_list import BoardList
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
from parser.quotation.quotes_list import QuotesList
from parser.quotation.quotes import Quotes
from parser.quotation.tick_chart import TickChart
from parser.quotation.top_board import TopBoard
from parser.quotation.transaction import Transaction
from parser.quotation.unusual import Unusual
from parser.quotation.volume_profile import VolumeProfile

__all__ = [
    'Auction',
    'BoardList',
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
    

# >0700
# 01 393939393939 c437 0200 # 01 393939393939 e355 0200
# 00 333939303031 c437 0200 # 00 333939303031 ae55 0200
# 02 383939303530 bf37 0200 # 02 383939303530 aa55 0200
# 00 333939303036 c437 0200 # 00 333939303036 554a 0200
# 01 303030363838 c437 0200 # 01 303030363838 f949 0200
# 01 303030333030 c437 0200 # 01 303030333030 f949 0200
# 01 383830303035 c337 0200 # 01 383830303035 b055 0200

# < 9493
# 92aaaaaaaaaaaa
# 1f812b7bbc50b941891a97478970c69193d9233a48619093b572a4c0054d18669229585c6e9213365ad20c7a4e900d5a3a8d9334800f9c0c7701973b5a91bd953a083e7d9293089d289c939393939393939391939393939393939393
# 6b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc9393
# 
# 93a0aaaaa3a3a2
# 1e810a733192603f917e3492308a7e34923dc69193b01c6a317c97938830eac0151721249139666324912b6f6afd1f005c9f3f02329e930c8a1881077f7f9793a8910d5c048e933e83399c93939393939393939193900ae39293939393
# 4a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a7331929393
# 
# 91abaaaaa3a6a3
# 9b98334b824b962d92299e429e3ac691932692222b429a93af160bc3311a6c972e2d419713224f923c6f239293930791179193939293939334912592939393939393939391939393939393939393
# 734b82734b829393734b82734b829393734b82734b829393734b82734b829393734b82734b829393734b82734b829393
# 
# 93a0aaaaa3a3a5
# 1e810d68b56cff63a8009a63a860da9193b42b29733c921c1957aa6ff270c103382ac4251c34cb2b535dba3c796c919393009f3e9b939395929393069a199b939393939393939391935d48c29393939393
# 4d68b54d68b593934d68b54d68b593934d68b54d68b593934d68b54d68b593934d68b54d68b593934c68b54c68b59393
# 
# 92a3a3a3a5abab
# 188106358379ba55b2329755b26ada9193903d7841942d1cfac7fbdec2247004821e0e49821f4f6692013f329293932296049093939293939316971797939393939393939391939393939393939393
# 463583463583939346358346358393934635834635839393463583463583939346358346358393934635834635839393
# 
# 92a3a3a3a0a3a3
# 1f813936ab6bd048b63a9548b66ada919354922b285f0e920b421192e12943c1271614a0290840a6176235b2240c229793930691189193939193939314923592939393939393939391939393939393939393
# 7936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab9393
# 
# 92ababa3a3a3a6
# d5803325b74718904f709b2b0c8d6716b13ec6919393355001789b030097498e48c037923897230f0e21923b2d0791939307b628b3939338973792939313918e93933a918e93933a929b91939393939393939393
# 7325b77325b793937325b77325b793937325b77325b793937325b77325b793937325b77325b793937325b77325b79393

# 93 -> 0  -> a3
# 92 -> 1  -> a2
# 91 -> 2  -> a1
# 90 -> 3  -> a0
# 97 -> 4  -> a7
# 96 -> 5  -> a6
# 95 -> 6  -> a5
# 94 -> 7  -> a4
# 9b -> 8  -> ab
# 9a -> 9  -> aa
# 99 -> 10
# 98 -> 11
# 9f -> 12
# 9e -> 13
# 9d -> 14
# 9c -> 15
# 83 -> 16
# 82 -> 17
# 81 -> 18
@register_parser(0x547) # TODO: 怪异编码
class TODO547(BaseParser):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception('stocks count must > 0')
        self.body = bytearray(struct.pack('<H', count))
        
        for market, code in stocks:
            self.body.extend(struct.pack('<B6sHH', market.value, code.encode('gbk'), 22234, 2))
        print('body: ', self.body.hex())

    @override
    def deserialize(self, data):
        print(struct.unpack('<H', data[:2]))
        print('data: ', data.hex())
            
        return data