import struct
from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x123D, 1)
class StockBarCount(BaseParser):
    def __init__(self, market: MARKET, code: str, count: int = 500):
        self.body = struct.pack('<H6s20xI10x', market.value, code.encode('gbk'), count)

    def deserialize(self, data):
        if len(data) < 28:
            return []
        # header: market(2) + code(6) + padding(16) + 4 bytes
        market = struct.unpack_from('<H', data, 0)[0]
        code = data[2:8].decode('ascii', errors='replace').rstrip('\x00')
        # bar entries
        header_length = 28
        bar_length = 22
        bars = []
        pos = header_length
        while pos + bar_length <= len(data):
            row = data[pos:pos + bar_length]
            offset_val, = struct.unpack_from('<I', row, 0)
            price, = struct.unpack_from('<f', row, 4)
            vol, = struct.unpack_from('<I', row, 8)
            change, = struct.unpack_from('<i', row, 12)
            if offset_val == 0 and vol == 0:
                break
            bars.append({
                'offset': offset_val,
                'price': round(price, 2),
                'vol': vol,
                'change': change,
            })
            pos += bar_length
        return bars
