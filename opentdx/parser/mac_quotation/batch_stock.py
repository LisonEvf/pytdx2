import struct
from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x122B, 1)
class BatchStockData(BaseParser):
    def __init__(self, market: MARKET, code: str):
        header = bytes.fromhex('ffffffffff58ff070000000200000000000000000100')
        self.body = header + struct.pack('<H', market.value) + code.encode('ascii') + b'\x00' * 16

    def deserialize(self, data):
        if len(data) < 30:
            return None
        # skip batch header (22 bytes), then stock record
        pos = 22
        market_val, = struct.unpack_from('<H', data, pos)
        code = data[pos + 2:pos + 8].decode('ascii', errors='replace').rstrip('\x00')
        name = data[pos + 24:pos + 32].decode('gbk', errors='replace').rstrip('\x00')
        result = {
            'market': market_val,
            'code': code,
            'name': name,
        }
        # parse OHLCV floats after name region
        float_start = pos + 32
        if float_start + 5 * 4 <= len(data):
            open_p, high, low, close, _ = struct.unpack_from('<5f', data, float_start)
            result.update({
                'open': round(open_p, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
            })
        return result
