import struct
from opentdx._typing import override

from opentdx.const import MARKET
from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import get_price


@register_parser(0x51d) # TODO: 未完成
class IndexInfo(BaseParser): 
    def __init__(self, market: MARKET, code: str):
        self.body = struct.pack(u'<H6sI', market.value, code.encode('gbk'), 0)

    @override
    def deserialize(self, data):
        count, market, code, active = struct.unpack('<IB6sH', data[:13])
        pos = 13

        close, pos = get_price(data, pos)
        pre_close_diff, pos = get_price(data, pos)
        open_diff, pos = get_price(data, pos)
        high_diff, pos = get_price(data, pos)
        low_diff, pos = get_price(data, pos)
        maybe_server_time, pos = get_price(data, pos)
        maybe_after_hour, pos = get_price(data, pos)
        vol, pos = get_price(data, pos)
        maybe_cur_vol, pos = get_price(data, pos)

        amount, = struct.unpack('<f', data[pos: pos + 4])
        pos += 4

        a, pos = get_price(data, pos)
        b, pos = get_price(data, pos)
        open_amount, pos = get_price(data, pos)
        d, pos = get_price(data, pos)
        e, pos = get_price(data, pos)
        f, pos = get_price(data, pos)
        up_count, pos = get_price(data, pos)
        down_count, pos = get_price(data, pos)
        g, pos = get_price(data, pos)
        h, pos = get_price(data, pos)
        i, pos = get_price(data, pos)
        j, pos = get_price(data, pos)
        k, pos = get_price(data, pos)
        l, pos = get_price(data, pos)
        m, pos = get_price(data, pos)
        n, pos = get_price(data, pos)
        o, pos = get_price(data, pos)
        p, pos = get_price(data, pos)

        # print(code.decode('gbk'),format_time(maybe_server_time), '{:2}'.format(maybe_after_hour), '{:8}'.format(maybe_cur_vol), '|','{:9}'.format(a), '{:9}'.format(b), '{:9}'.format(open_amount), '{:7}'.format(d), '{:9}'.format(e), '{:9}'.format(f), '|', g, h, i, j, k, l, m, n, o, p)
        
        orders = []
        for _ in range(count):
            min_point, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)
            min_vol, pos = get_price(data, pos)

            orders.append({
                'price': min_point,
                'unknown': unknown,
                'vol': min_vol,
            })
            
        return {
            'market': MARKET(market),
            'code': code.decode('gbk'),
            'active': active,
            'pre_close': close + pre_close_diff,
            'diff': -pre_close_diff,
            'close': close,
            'open': close + open_diff,
            'high': close + high_diff,
            'low': close + low_diff,
            'vol': vol,
            'amount': amount,
            'up_count': up_count,
            'down_count': down_count
        }