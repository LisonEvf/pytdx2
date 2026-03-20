import struct
from typing import override

from const import MARKET
from parser.baseParser import BaseParser, register_parser


@register_parser(0x44d) # TODO: 2Unknown
class List(BaseParser):
    def __init__(self, market: MARKET, start: int = 0, count: int = 1600):
        self.body = struct.pack(u'<H3I', market.value, start, count, 0)

    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])
        
        stocks = []
        for i in range(count):
            pos = 2 + i * 37
            code, vol, name, unknown1, decimal_point, pre_close, unknown2, unknown3 = struct.unpack('<6sH16sfBfHH', data[pos: pos + 37])

            # print(name.decode('gbk', errors='ignore').rstrip('\x00'), unknown1, unknown2, unknown3)
            # print(data[pos: pos + 37].hex())
            stocks.append({
                'code': code.decode('gbk', errors='ignore').rstrip('\x00'),
                'vol': vol,
                'name': name.decode('gbk', errors='ignore').rstrip('\x00'),
                'decimal_point': decimal_point,
                'pre_close': pre_close,
                'unknown1': [unknown1, unknown2, unknown3],
            })

        return stocks