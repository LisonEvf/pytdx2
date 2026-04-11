import struct
from typing import override

from opentdx.const import EX_CATEGORY
from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import unpack_futures

@register_parser(0x23fa, 1)
class QuotesSingle(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B9s', category.value, code.encode('gbk'))
    
    @override
    def deserialize(self, data):
        return unpack_futures(data, 9)