import struct
from typing import override

from const import EX_CATEGORY
from parser.base_parser import BaseParser, register_parser
from utils.help import unpack_futures

@register_parser(0x23fb, 1)
class Quotes(BaseParser):
    def __init__(self, futures: list[EX_CATEGORY, str] = []):
        length = len(futures)
        if length <= 0:
            raise Exception('futures count must > 0')
        self.body = bytearray(struct.pack('<HHHHH', 2, 3148, 0, 600, length)) # TODO
        
        for category, code in futures:
            self.body.extend(struct.pack('<B23s', category.value, code.encode('gbk')))

    @override
    def deserialize(self, data):
        u, _, count = struct.unpack('<IIH', data[:10])
        results = []
        for i in range(count):
            results.append(unpack_futures(data[314 * i + 10: 314 * i + 324]))
        return results