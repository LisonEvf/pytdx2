import struct
from typing import override

from const import MARKET
from parser.base_parser import BaseParser, register_parser
from utils.help import get_price


@register_parser(0x51c)
class IndexMomentum(BaseParser):
    def __init__(self, market: MARKET, code: str):
        self.body = struct.pack(u'<H6s', market.value, code.encode('gbk'))
    
    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])
        pos = 2

        start_mom = 0
        result = []
        for _ in range(count):
            mom, pos = get_price(data, pos)
            start_mom += mom
            result.append(start_mom)
        return result