import struct
from opentdx._typing import override

from opentdx.const import EX_MARKET, PERIOD
from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import to_datetime

@register_parser(0x23ff, 1)
class K_Line(BaseParser):
    def __init__(self, market: EX_MARKET, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800):
        self.body = struct.pack('<B9sHHIH', market.value, code.encode('gbk'), period.value, times, start, count)
        
    @override
    def deserialize(self, data):
        market, name, period, times, _, count = struct.unpack('<B9sHHIH', data[:20])

        minute_category = period < 4 or period == 7 or period == 8

        results = []
        for i in range(count):
            date_num, open, high, low, close, amount, vol, _ = struct.unpack('<IfffffIf', data[20 + 32 * i: 20 + 32 * i + 32])
            
            results.append({
                'date_time': to_datetime(date_num, minute_category),
                'open': open,
                'high': high,
                'low': low,
                'close': close,
                'amount': amount,
                'vol': vol,
            })
        return results