import struct
from typing import override

from const import MARKET
from parser.base_parser import BaseParser, register_parser


@register_parser(0x450) # TODO: 2Unknown
class List2(BaseParser):
    def __init__(self, market: MARKET, start):
        self.body = struct.pack(u'<HH', market.value, start)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])

        stocks = []
        for i in range(count):
            pos = 2 + i * 29
            code, vol, name, unknown1, _, decimal_point, pre_close, unknown2, unknown3 = struct.unpack('<6sH8sHHBfHH', data[pos: pos + 29])

            stocks.append({
                'code': code.decode('gbk', errors='ignore').rstrip('\x00'),
                'vol': vol,
                'name': name.decode('gbk', errors='ignore').rstrip('\x00'),
                'decimal_point': decimal_point,
                'pre_close': pre_close,
                'unknown1': [unknown1, unknown2, unknown3],
            })

        return stocks