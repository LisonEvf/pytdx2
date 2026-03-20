import struct
from typing import override

from parser.baseParser import BaseParser, register_parser

@register_parser(0x23f5, 1)
class List(BaseParser):
    def __init__(self, start, count):
        self.body = struct.pack('<IH', start, count)

    @override
    def deserialize(self, data):
        start, count = struct.unpack('<IH', data[:6])
        
        instruments = []
        for i in range(count):
            market, category, u3, u4, code, name, u5, u6, u7, u8, u9, u10, u11, u12, u13, u14 = struct.unpack('<BBBH9s26sffHHHHHHHH', data[i * 64 + 6: i * 64 + 70])

            instruments.append({
                'market': market,
                'category': category,
                'code': code.decode('gbk').replace('\x00', ''),
                'desc': [u3, u4, u5, u6, u7, u8, u9, u10, u11, u12, u13, u14],
                'name': name.decode('gbk', errors='ignore').replace('\x00', ''),
            })
        
        return instruments