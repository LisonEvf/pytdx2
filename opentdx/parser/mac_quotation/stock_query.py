import struct
from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x122A, 1)
class StockQuery(BaseParser):
    def __init__(self, market: MARKET, code: str, flag: int = 1, unk: int = 0):
        self.body = struct.pack('<H6s16xB4xB10x', market.value, code.encode('gbk'), flag, unk)

    def deserialize(self, data):
        if len(data) < 40:
            return None
        # header: count(4) + unknown(4)
        count, = struct.unpack_from('<I', data, 0)
        if count == 0:
            return None
        # per-stock record starts at offset 8
        pos = 8
        market_val, = struct.unpack_from('<H', data, pos)
        code = data[pos + 2:pos + 8].decode('ascii', errors='replace').rstrip('\x00')
        name = data[pos + 24:pos + 32].decode('gbk', errors='replace').rstrip('\x00')
        # float fields after name region
        # price data starts approximately at pos+32 area
        result = {
            'market': market_val,
            'code': code,
            'name': name,
        }
        # parse float fields if available
        float_start = pos + 80
        if float_start + 4 * 4 <= len(data):
            last_close, = struct.unpack_from('<f', data, float_start)
            open_price, = struct.unpack_from('<f', data, float_start + 4)
            high, = struct.unpack_from('<f', data, float_start + 8)
            low, = struct.unpack_from('<f', data, float_start + 12)
            close, = struct.unpack_from('<f', data, float_start + 16)
            result.update({
                'pre_close': round(last_close, 2),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
            })
        return result
