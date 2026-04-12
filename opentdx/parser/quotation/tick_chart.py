import struct
from typing import override

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import get_price


@register_parser(0x537)
class TickChart(BaseParser):
    def __init__(self, market: MARKET, code: str, start: int = 0, count: int = 0xba00):
        self.body = bytearray(struct.pack('<H6sHH', market.value, code.encode('gbk'), start, count))
        
    @override
    def deserialize(self, data):
        num, _ = struct.unpack('<HH', data[:4])

        result = []
        pos = 4
        start_price = 0
        start_avg = 0
        for _ in range(num):
            price, pos = get_price(data, pos)
            avg, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)

            result.append({
                'price': start_price + price,
                'avg': start_avg + avg,
                'vol': vol,
            })
            if start_price == 0:
                start_price = price
            if start_avg == 0:
                start_avg = avg
        return result