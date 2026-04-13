from datetime import time
import struct
from opentdx._typing import override

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import get_price


@register_parser(0xfc5)
class Transaction(BaseParser):
    def __init__(self, market: MARKET, code: str, start: int, count: int):
        self.body = struct.pack(u'<H6sHH', market.value, code.encode('gbk'), start, count)

    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])
        pos = 2

        last_price = 0
        transactions = []
        for _ in range(count):
            minutes, = struct.unpack('<H', data[pos: pos + 2])
            pos += 2

            price, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            trans, pos = get_price(data, pos)
            buy_sell, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)

            last_price += price
            transactions.append({
                'time': time(minutes // 60 % 24, minutes % 60),
                'price': last_price,
                'vol': vol,
                'trans': trans,
                'action': ['BUY', 'SELL', 'NEUTRAL'][buy_sell],
                'unknown': unknown,
            })

        return transactions