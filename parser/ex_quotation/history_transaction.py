from datetime import date, time
import struct
from typing import override

from const import EX_CATEGORY
from parser.base_parser import BaseParser, register_parser

# >1224 e8013501 2a 543030390000000000000000000000000000000000000000000000000000000000000000000000 000000007800
# >1224 90013501 4a 4141504c0000000000000000000000000000000000000000000000000000000000000000000000 000000007800
# >1224 57023501 4a 41414d490000000000000000000000000000000000000000000000000000000000000000000000 000000007800
# >1224 a5d93401 4a 414143495500000000000000000000000000000000000000000000000000000000000000000000 000000007800
# >1224 e9013501 1b 4345534d0000000000000000000000000000000000000000000000000000000000000000000000 780000008403
# >1224 e9013501 1b 4345534d0000000000000000000000000000000000000000000000000000000000000000000000 fc0300008403
# >1224 ee013501 1f 303030323500000000000000000000000000000000000000000000000000000000000000000000 000000007800
@register_parser(0x2412, 1)
class HistoryTransaction(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str, date: date):
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack('<IB43sH', date, category.value, code.encode('gbk'), 0x78)
        
    @override
    def deserialize(self, data):
        category, name, date, start_price, _, _, count = struct.unpack('<B39sIfIIH', data[:58])

        results = []
        for _ in range(count):
            minutes, price, vol, u, buy_sell = struct.unpack('<HIIIH', data[58 + 16 * _ : 58 + 16 * _ + 16])
            results.append({
                'time': time(minutes // 60 % 24, minutes % 60),
                'price': price,
                'vol': vol,
                'action': ['BUY', 'SELL', 'NEUTRAL'][buy_sell]
            })

        return results