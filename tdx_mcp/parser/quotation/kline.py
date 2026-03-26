import struct
from typing import override

from tdx_mcp.const import MARKET, PERIOD, ADJUST
from tdx_mcp.parser.baseParser import BaseParser, register_parser
from tdx_mcp.utils.help import get_price, to_datetime


@register_parser(0x523)
class K_Line(BaseParser):
    def __init__(self, market: MARKET, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800, fq: ADJUST= ADJUST.NONE):
        self.body = struct.pack(u'<H6sHHHHH8s', market.value, code.encode('gbk'), period.value, times, start, count, fq.value, b'')
        
        self.period = period
        
    @override
    def deserialize(self, data):
        data_len = len(data)
        count, = struct.unpack('<H', data[:2])
        pos = 2

        minute_category = self.period.value < 4 or self.period.value == 7 or self.period.value == 8

        bars = []
        for _ in range(count):
            date_num, = struct.unpack('<I', data[pos: pos + 4])
            pos += 4
            date_time = to_datetime(date_num, minute_category)
            
            open, pos = get_price(data, pos)
            close, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)
            
            vol, amount = struct.unpack('<ff', data[pos: pos + 8])
            pos += 8

            upCount = 0
            downCount = 0
            if pos < data_len:
                try:
                    try_date, = struct.unpack('<I', data[pos: pos + 4])
                    try_date_time = to_datetime(try_date, minute_category)
                    if try_date_time.year < date_time.year:
                        raise ValueError()
                except ValueError:
                    upCount, downCount = struct.unpack('<HH', data[pos: pos + 4])
                    pos += 4
            
            bar = {
                'datetime': date_time,
                'open': open,
                'close': close,
                'high': high,
                'low': low,
                'vol': vol,
                'amount': amount,
            }
            if upCount != 0 or downCount != 0:
                bar['up_count'] = upCount
                bar['down_count'] = downCount
            bars.append(bar)
            
        return bars