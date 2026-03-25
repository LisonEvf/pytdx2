import struct

from tdx_mcp.const import EX_CATEGORY
from tdx_mcp.parser.baseParser import register_parser
from tdx_mcp.parser.ex_quotation.quotes import Quotes

@register_parser(0x23fb, 1)
class Quotes2(Quotes):
    def __init__(self, futures: list[EX_CATEGORY, str] = []):
        length = len(futures)
        if length <= 0:
            raise Exception('futures count must > 0')
        self.body = bytearray(struct.pack('<HHHHH', 2, 3148, 0, 600, length)) # TODO
        
        for category, code in futures:
            self.body.extend(struct.pack('<B23s', category.value, code.encode('gbk')))