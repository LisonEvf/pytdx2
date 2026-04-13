from datetime import date, time
import struct
from opentdx._typing import override

from opentdx.const import EX_MARKET
from opentdx.parser.baseParser import BaseParser, register_parser

# > 8c24 e0013501 1c 434a4c3800000000000000000000000000000000000000 000000000000 2f49
# > 8c24 31013501 1c 434a4c3800000000000000000000000000000000000000 393938f94902 0001
# > 8c24 73253501 1c 434a4c3800000000000000000000000000000000000000 000000000000 2f49
# > 8c24 f8013501 1c 434a4c3800000000000000000000000000000000000000 303530aa5502 0000
# > 8c24 94013501 4a 46484e2d43000000000000000000000000000000000000 000000000000 0001
#        94013501 4a 46484e2d43000000000000000000000000000000000000 000000000000 0001
@register_parser(0x248c, 1) # TODO 后8位不明所以
class HistoryTickChart(BaseParser):
    def __init__(self, market: EX_MARKET, code: str, date: date):
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack('<IB23s6sH', date, market.value, code.encode('gbk'), b'', 0)

    @override
    def deserialize(self, data):
        market, name, date, avg_price, _, _, count = struct.unpack('<B23sIfIIH', data[:42])
        charts = []
        for i in range(count):
            minutes, price, avg ,vol, u = struct.unpack('<HffII', data[42 + 18 * i : 42 + 18 * i + 18])
            charts.append({
                'time': time(minutes // 60 % 24, minutes % 60),
                'price': price,
                'avg': avg,
                'vol': vol
            })
        return charts