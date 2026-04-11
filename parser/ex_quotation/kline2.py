import struct
from typing import override

from const import EX_MARKET, PERIOD
from parser.baseParser import BaseParser, register_parser
from utils.help import to_datetime

@register_parser(0x2489, 1)
class K_Line2(BaseParser):
    def __init__(self, market: EX_MARKET, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800):
        self.body = struct.pack('<B23sHHII16x', market.value, code.encode('gbk'), period.value, times, start, count)

    @override
    def deserialize(self, data):
        market, name, period, times, start, _, _, count = struct.unpack('<B23sHHIIIH', data[:42])

        minute_category = period < 4 or period == 7 or period == 8

        results = []
        for i in range(count):
            date_num, open, high, low, close, amount, vol, _ = struct.unpack('<IfffffII', data[42 + 32 * i: 42 + 32 * i + 32])
            
            results.append({
                'time': to_datetime(date_num, minute_category),
                'open': open,
                'high': high,
                'low': low,
                'close': close,
                'amount': amount,
                'vol': vol,
            })
        return results