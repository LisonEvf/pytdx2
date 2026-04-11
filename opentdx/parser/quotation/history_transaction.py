from datetime import date, time
import struct
from typing import override

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import get_price


@register_parser(0xfb5)
class HistoryTransaction(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date, start: int, count: int):
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IH6sHH', date, market.value, code.encode('gbk'), start, count)

    @override
    def deserialize(self, data):
        count, pre_close = struct.unpack('<Hf', data[:6])
        pos = 6

        last_price = 0
        transactions = []
        for _ in range(count):
            minutes, = struct.unpack('<H', data[pos: pos + 2])
            pos += 2

            price, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            buy_sell, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)

            last_price += price
            transactions.append({
                'time': time(minutes // 60 % 24, minutes % 60),
                'price': last_price,
                'vol': vol,
                'action': ['BUY', 'SELL', 'NEUTRAL'][buy_sell],
                'unknown': unknown,
            })

        return transactions