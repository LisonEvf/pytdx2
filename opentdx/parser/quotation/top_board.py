import struct
from opentdx._typing import override

from opentdx.const import CATEGORY, MARKET
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x53f)
class TopBoard(BaseParser):
    def __init__(self, category: CATEGORY, size: int = 20):
        self.body = struct.pack('<BB7sB', category.value, 5, bytes.fromhex('000000000100'), size)
    @override
    def deserialize(self, data):
        size, = struct.unpack('<B', data[:1])
        pos = 1

        result = {
            'increase': [],
            'decrease': [],
            'amplitude': [],
            'rise_speed': [],
            'fall_speed': [],
            'vol_ratio': [],
            'pos_commission_ratio': [],
            'neg_commission_ratio': [],
            'turnover': [],
        }

        for item in result:
            for _ in range(size):
                market, code, price, value = struct.unpack('<B6sff', data[pos: pos + 15])
                pos += 15

                result[item].append({
                    'market': MARKET(market),
                    'code': code.decode('gbk'),
                    'price': price,
                    'value': value,
                })
         
        return result