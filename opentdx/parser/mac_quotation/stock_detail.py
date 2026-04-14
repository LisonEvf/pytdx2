import struct
from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x122F, 1)
class StockDetail(BaseParser):
    def __init__(self, market: MARKET, code: str):
        self.body = struct.pack('<H6s24xBBB9x', market.value, code.encode('gbk'), 0x32, 0, 1)

    def deserialize(self, data):
        if len(data) < 28:
            return []
        # header: market(2) + code(6) + padding(16) + 4 bytes
        market = struct.unpack_from('<H', data, 0)[0]
        code = data[2:8].decode('ascii', errors='replace').rstrip('\x00')
        # tick entries start after header
        # find the start of tick data by looking for the pattern
        # header is approximately 28 bytes
        header_length = 28
        tick_length = 18
        ticks = []
        pos = header_length
        while pos + tick_length <= len(data):
            row = data[pos:pos + tick_length]
            time_val, = struct.unpack_from('<H', row, 0)
            price, = struct.unpack_from('<f', row, 4)
            vol1, = struct.unpack_from('<I', row, 8)
            vol2, = struct.unpack_from('<I', row, 12)
            direction, = struct.unpack_from('<H', row, 16)
            if time_val == 0 and price == 0:
                break
            ticks.append({
                'time': time_val,
                'price': round(price, 2),
                'vol1': vol1,
                'vol2': vol2,
                'direction': direction,
            })
            pos += tick_length
        return ticks
