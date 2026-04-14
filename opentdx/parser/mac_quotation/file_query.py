import struct
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x1215, 1)
class FileList(BaseParser):
    def __init__(self, filename: str, offset: int = 0):
        self.body = struct.pack('<I70s30x', offset, filename.encode('gbk'))

    def deserialize(self, data):
        if len(data) < 9:
            return None
        offset, size = struct.unpack_from('<II', data, 0)
        flag = data[8]
        file_hash = data[9:41].decode('ascii', errors='replace').rstrip('\x00')
        return {
            'offset': offset,
            'size': size,
            'flag': flag,
            'hash': file_hash,
        }


@register_parser(0x1217, 1)
class FileDownload(BaseParser):
    def __init__(self, filename: str, index: int = 1, offset: int = 0, size: int = 30000):
        self.body = struct.pack('<III70s30x', index, offset, size, filename.encode('gbk'))

    def deserialize(self, data):
        if len(data) < 8:
            return None
        index, size = struct.unpack_from('<II', data, 0)
        content = data[8:]
        try:
            text = content.decode('gbk', errors='replace')
        except Exception:
            text = content.hex()
        return {
            'index': index,
            'size': size,
            'content': text,
        }
