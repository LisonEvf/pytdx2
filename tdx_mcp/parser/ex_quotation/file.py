import struct

from tdx_mcp.parser.baseParser import register_parser
from tdx_mcp.parser.quotation import file

@register_parser(0x2458, 1)
class Meta(file.Meta):
    pass
    
@register_parser(0x2459, 1)
class Download(file.Download):
    def __init__(self, file_name: str, start: int = 0, size: int = 0x7530):
        self.body = struct.pack('<II40s', start, size, file_name.encode('gbk'))
