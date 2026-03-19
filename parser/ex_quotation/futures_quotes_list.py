import struct

from const import EX_CATEGORY
from parser.base_parser import register_parser
from parser.ex_quotation.quotes import Quotes

@register_parser(0x2484, 1)
class Futures_QuotesList(Quotes):
    def __init__(self, category: EX_CATEGORY, start: int = 0, count: int = 100):
        self.body = struct.pack('<BHHHH', category.value, 0, start, count, 1) 