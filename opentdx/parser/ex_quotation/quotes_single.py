import struct
from opentdx._typing import override

from opentdx.const import EX_MARKET
from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import unpack_futures

@register_parser(0x23fa, 1)
class QuotesSingle(BaseParser):
    def __init__(self, market: EX_MARKET, code: str):
        self.body = struct.pack('<B9s', market.value, code.encode('gbk'))
    
    @override
    def deserialize(self, data):
        return unpack_futures(data, 9)