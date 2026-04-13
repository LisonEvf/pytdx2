import struct
from opentdx._typing import override

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser

# > d10f 0000 303030393231 0000000000000000000000000000000001001400000000010000000000 0c2b080002000f000f00470501000030303039323100000000

@register_parser(0xfd1)
class ChartSampling(BaseParser):
    def __init__(self, market: MARKET, code: str):
        self.body = bytearray(struct.pack('<H6s', market.value, code.encode('gbk')))
        
        self.body.extend(bytearray().fromhex('0000000000000000000000000000000001001400000000010000000000'))
    
    @override
    def deserialize(self, data):
        if len(data) < 42:
            return []

        market, code = struct.unpack('<H6s', data[:8])
        interval, pre_close, count = struct.unpack('<HfH', data[34:42])

        prices = []
        available_count = max(0, (len(data) - 42) // 4)
        actual_count = min(count, available_count)
        for i in range(actual_count):
            p, = struct.unpack('<f', data[i * 4 + 42: i * 4 + 46])
            prices.append(p)
            
        return prices
