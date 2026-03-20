import struct
from typing import override

from parser.baseParser import BaseParser, register_parser

@register_parser(0x2422, 1)
class Table(BaseParser):
    def __init__(self, start: int = 0, mode: int = 1):
        self.body = bytearray(struct.pack('<II16s85xB16x', start, 0, bytes.fromhex('00781f0e6a37447b502b7c0d01404c0a'), mode))

    @override
    def deserialize(self, data):
        start, = struct.unpack('<I', data[35:39])
        count, ctx_len = struct.unpack('<II', data[161:169])
        ctx = data[169:].decode('gbk',errors='ignore').replace('\x00', '')
        return start, count, ctx