from datetime import date, time
import struct
from typing import override

from tdx_mcp.const import MARKET
from tdx_mcp.parser.baseParser import BaseParser, register_parser
from tdx_mcp.utils.help import get_price


@register_parser(0xfc6)
class HistoryTransactionWithTrans(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date, start: int, count: int):
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IH6sHH', date, market.value, code.encode('gbk'), start, count)

    @override
    def deserialize(self, data):
        count, pre_close = struct.unpack('<Hf', data[:6])
        pos = 6

        last_price = 0
        result = []
        for _ in range(count):
            minutes, = struct.unpack('<H', data[pos: pos + 2])
            pos += 2

            price, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            num, pos = get_price(data, pos)

            buy_sell, = struct.unpack('<H', data[pos: pos + 2])
            pos += 2

            last_price += price
            result.append({
                'time': time(minutes // 60 % 24, minutes % 60),
                'price': last_price,
                'vol': vol,
                'num': num,
                'action': ['BUY', 'SELL', 'NEUTRAL'][buy_sell],
            })
        return result