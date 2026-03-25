import struct

from tdx_mcp.const import EX_CATEGORY, SORT_TYPE
from tdx_mcp.parser.baseParser import register_parser
from tdx_mcp.parser.ex_quotation.quotes import Quotes

@register_parser(0x2484, 1)
class QuotesList(Quotes):
    def __init__(self, category: EX_CATEGORY, start: int = 0, count: int = 100, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False):
        self.body = struct.pack('<BHHHH', category.value, sortType.value, start, count, 2 if reverse else 1) 