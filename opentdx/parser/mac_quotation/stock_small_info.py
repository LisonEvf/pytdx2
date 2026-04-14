import struct
from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x123E, 1)
class StockSmallInfo(BaseParser):
    def __init__(self, market: MARKET, code: str, period: int = 5, flag: int = 1):
        self.body = struct.pack('<H6s20xHH6x', market.value, code.encode('gbk'), period, flag)

    def deserialize(self, data):
        if len(data) < 28:
            return []
        # header: market(2) + code(6) + padding(16) + some fields
        market_val, = struct.unpack_from('<H', data, 0)
        code = data[2:8].decode('ascii', errors='replace').rstrip('\x00')
        # find tick entries - each has: index(2B) + price(4B float) + avg(4B float) + vol(4B)
        header_length = 28
        tick_length = 14
        ticks = []
        pos = header_length
        while pos + tick_length <= len(data):
            row = data[pos:pos + tick_length]
            idx, = struct.unpack_from('<H', row, 0)
            price, = struct.unpack_from('<f', row, 2)
            avg, = struct.unpack_from('<f', row, 6)
            vol, = struct.unpack_from('<I', row, 10)
            if vol == 0 and price == 0:
                break
            ticks.append({
                'index': idx,
                'price': round(price, 2),
                'avg': round(avg, 2),
                'vol': vol,
            })
            pos += tick_length
        return ticks
