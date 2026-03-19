from datetime import date
import struct
from typing import override

from const import MARKET
from parser.base_parser import BaseParser, register_parser
from utils.help import get_price


@register_parser(0xfb4)
class HistoryOrders(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date):
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IB6s', date, market.value, code.encode('gbk'))

    @override
    def deserialize(self, data):
        count, pre_close = struct.unpack('<Hf', data[:6])
        pos = 6

        orders = []
        last_price = 0
        for _ in range(count):
            price, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)

            last_price += price

            orders.append({
                'price': last_price,
                'unknown': unknown, # 像是大单笔数？
                'vol': vol,
            })
        return orders