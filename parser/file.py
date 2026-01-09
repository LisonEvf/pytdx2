import struct
from typing import override
from const import BLOCK_FILE_TYPE
from parser.baseparser import BaseParser, register_parser
import six

@register_parser(0x6b9)
class Download(BaseParser):
    def __init__(self, file_name: str, start: int = 0, size: int = 0x7530):
        if type(file_name) is six.text_type:
            file_name = file_name.encode("utf-8")
        self.body = struct.pack('<II100s', start, size, file_name)

    @override
    def deserialize(self, data):
        return {
            'size': struct.unpack('<I', data[:4])[0],
            'data': data[4:]
        }

@register_parser(0x2c5)
class Meta(BaseParser):
    def __init__(self, file_name: str):
        self.body = struct.pack('<40s', file_name.encode("utf-8"))

    @override
    def deserialize(self, data):
        (size, unknow1, hash_value, unknow2) = struct.unpack(u"<I1s32s1s", data)
        return {
            "size": size,
            "hash_value" : hash_value,
            "unknow1" : unknow1,
            "unknow2" : unknow2
        }

class Block(Download):
    def __init__(self, block_file_type: BLOCK_FILE_TYPE, start: int, size: int):
        super().__init__(block_file_type.value, start, size)