import struct
from typing import override

from tdx_mcp.const import EX_CATEGORY
from tdx_mcp.parser.baseParser import BaseParser, register_parser
from tdx_mcp.utils.help import unpack_futures

@register_parser(0x23fa, 1)
class QuotesSingle(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B9s', category.value, code.encode('gbk'))
    
    @override
    def deserialize(self, data):
        return unpack_futures(data, 9)