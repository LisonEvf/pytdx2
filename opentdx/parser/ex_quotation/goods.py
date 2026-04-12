from opentdx.parser.ex_quotation.category_list import CategoryList 
from opentdx.parser.ex_quotation.chart_sampling import ChartSampling 
from opentdx.parser.ex_quotation.count import Count
from opentdx.parser.ex_quotation.history_tick_chart import HistoryTickChart 
from opentdx.parser.ex_quotation.history_transaction import HistoryTransaction 
from opentdx.parser.ex_quotation.kline import K_Line 
from opentdx.parser.ex_quotation.kline2 import K_Line2 
from opentdx.parser.ex_quotation.list import List 
from opentdx.parser.ex_quotation.quotes_list import QuotesList 
from opentdx.parser.ex_quotation.quotes_single import QuotesSingle 
from opentdx.parser.ex_quotation.quotes import Quotes
from opentdx.parser.ex_quotation.quotes2 import Quotes2
from opentdx.parser.ex_quotation.table_detail import TableDetail 
from opentdx.parser.ex_quotation.table import Table 
from opentdx.parser.ex_quotation.tick_chart import TickChart 

__all__ = [
    'CategoryList',
    'ChartSampling',
    'Count',
    'HistoryTickChart',
    'HistoryTransaction',
    'K_Line',
    'K_Line2',
    'List',
    'QuotesList',
    'QuotesSingle',
    'Quotes',
    'Quotes2',
    'TableDetail',
    'Table',
    'TickChart',
]

from opentdx.const import EX_CATEGORY, PERIOD
from opentdx.parser.baseParser import BaseParser, register_parser
import struct
from typing import override

@register_parser(0x122e, 1)
class kline2(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str, period: PERIOD, times: int = 1, mode: int = 0):
        self.body = struct.pack('<H22s11H', category.value, code.encode('gbk'), period.value, times, 0, 0, 700, mode, 257, 256, 0, 0, 0)

    @override
    def deserialize(self, data):
        category, code, u1, u2, count, _ = struct.unpack('<H22sHbHI', data[:33])

        for i in range(count):
            date_raw, a, b, c, d, e, f, g, h = struct.unpack('<I8f', data[i * 36 + 33: i * 36 + 69])
            print(date_raw, a, b, c, d, e, f, g, h)
        # print(data.hex())
        return None

@register_parser(0x23f6, 1)
class f23f6(BaseParser):
    def __init__(self):
        self.body = struct.pack('<HHH', 0, 0, 500)

    @override
    def deserialize(self, data):
        start, count = struct.unpack('<IH', data[:6])

        result = []
        for i in range(count):
            z = struct.unpack('<B8sB12H', data[i * 34 + 6: i * 34 + 40])
            print(z)

        return None

# @register_parser(0x240b, 1)
# class Chart(BaseParser): # 疑似废弃旧接口
#     def __init__(self, category: EX_CATEGORY, code: str):
#         self.body = struct.pack('<B9s', category.value, code.encode('gbk'))

#     @override
#     def deserialize(self, data):
#         category, code, count = struct.unpack('<B9sH', data[:12])

#         result = []
#         for i in range(count):
#             minutes, price, avg, vol, _ = struct.unpack('<HffII', data[i * 18 + 12: i * 18 + 30])
#             result.append({
#                 'time': time(minutes // 60, minutes % 60),
#                 'price': price,
#                 'avg': avg,
#                 'vol': vol
#             })
#         return result
    


# > 5424e5bb1c2fafe525941f32c6e5d53dfb415b734cc9cdbf0ac91f3b71a6861a5dce67c7dd2b6f5552dfef9257c6ad5547831f32c6e5d53dfb411f32c6e5d53dfb41a9325ac935dc0837335a16e4ce17c1bb
# TODO


@register_parser(0x2487, 1)
class f2487(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B23s', category.value, code.encode('gbk'))

    @override
    def deserialize(self, data):
        category, code = struct.unpack('<B23s', data[:24])
        
        active, pre_close, open, high, low, close, u1, price = struct.unpack('<I7f', data[24:56])
        vol, curr_vol, amount = struct.unpack('<IIf', data[56:68])
        
        a = struct.unpack('<4I', data[68:84])
        b = struct.unpack('<HII24fB10fHB', data[164:])
        print(a,b)
        print(data[84:164].hex())
        
        return {
            'category': EX_CATEGORY(category), 
            'code': code.decode('gbk').replace('\x00', ''), 
            'active': active, 
            'pre_close': pre_close, 
            'open': open, 
            'high': high, 
            'low': low, 
            
            'vol': vol, 
            'curr_vol': curr_vol, 
            'amount': amount, 
        }

# > 8824 22 3030303031300000000000000000000000000000000000 0000 0000 3700 0000000000000000
@register_parser(0x2488, 1) # TODO
class f2488(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B23sIHII', category.value, code.encode('gbk'), 0, 55, 0, 0)

    @override
    def deserialize(self, data):
        category, code, count = struct.unpack('<B35sH', data[:38])
        print(EX_CATEGORY(category), code.decode('gbk').replace('\x00', ''))

        for i in range(count):
            z = struct.unpack('<I6H', data[i * 16 + 38: i * 16 + 54])
            print(z)
        return None
    
@register_parser(0x2562, 1)
class f2562(BaseParser):
    def __init__(self, market: int, start: int = 0, count: int = 600):
        self.body = struct.pack(u'<HII', market, start, count)

    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])
        result = []
        
        for i in range(count):
            category, name, u, index, switch, u2, u3, u4, u5, u6 = struct.unpack('<H23sHIBfffHH', data[48 * i + 2: 48 * i + 50])
            result.append({
                'name': name.decode('gbk').replace('\x00', ''),
                'category': category,
                'u': u,
                'index': index,
                'switch': switch,
                'code': [u2, u3, u4, u5, u6]
            })
        return result