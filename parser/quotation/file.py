import struct
from typing import override
from const import BLOCK_FILE_TYPE
from parser.baseParser import BaseParser, register_parser

@register_parser(0x6b9)
class Download(BaseParser):
    def __init__(self, file_name: str, start: int = 0, size: int = 0x7530):
        self.body = struct.pack('<II300s', start, size, file_name.encode('gbk'))

    @override
    def deserialize(self, data):
        return {
            'size': struct.unpack('<I', data[:4])[0],
            'data': data[4:]
        }

@register_parser(0x2c5)
class Meta(BaseParser):
    def __init__(self, file_name: str):
        self.body = struct.pack('<40s', file_name.encode('gbk'))

    @override
    def deserialize(self, data):
        size, unknown1, hash_value, unknown2 = struct.unpack(u"<I1s32s1s", data)
        return {
            "size": size,
            "hash_value" : hash_value,
            "unknown1" : unknown1,
            "unknown2" : unknown2
        }

class Block(Download):
    def __init__(self, block_file_type: BLOCK_FILE_TYPE, start: int, size: int):
        super().__init__(block_file_type.value, start, size)