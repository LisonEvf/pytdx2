from datetime import date
import struct
from typing import override

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x44e)
class Count(BaseParser):
    def __init__(self, market: MARKET):
        today = date.today().year * 10000 + date.today().month * 100 + date.today().day
        self.body = struct.pack(u'<HI', market.value, today)

    @override
    def deserialize(self, data):
        return struct.unpack('<H', data)[0]