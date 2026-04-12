from datetime import time
import struct
from typing import override

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x56a)
class Auction(BaseParser):
    def __init__(self, market: MARKET, code: str, start: int = 0, count: int = 500):
        self.body = struct.pack(u'<H6sIIIII', market.value, code.encode('gbk'), 0, 3, 0, start, count)

    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])

        result = []
        for i in range(count):
            time_raw, price, matched, unmatched, u, second = struct.unpack('<HfIIBB', data[i * 16 + 2: i * 16 + 18])
            result.append({
                'time': time(time_raw // 60, time_raw % 60, second),
                'price': price,
                'matched': matched,
                'unmatched': unmatched
            })
        return result