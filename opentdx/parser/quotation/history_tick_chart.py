from datetime import date
import struct
from typing import override

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import get_price


@register_parser(0xfeb)
class HistoryTickChart(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date):
        date = -date.year * 10000 - date.month * 100 - date.day
        self.body = struct.pack(u'<iB6s', date, market.value, code.encode('gbk'))

    @override
    def deserialize(self, data):
        count, m, n = struct.unpack('<HII', data[:10])
        pos = 10

        result = []
        start_price = 0
        avg_price = 0
        for _ in range(count):
            price, pos = get_price(data, pos)
            avg, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)

            result.append({
                'price': start_price + price,
                'avg': avg_price + avg,
                'vol': vol,
            })
            if start_price == 0:
                start_price = price
            if avg_price == 0:
                avg_price = avg
        return result