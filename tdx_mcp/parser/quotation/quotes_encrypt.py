from datetime import time
import struct
from typing import override

from tdx_mcp.const import MARKET
from tdx_mcp.parser.baseParser import BaseParser, register_parser
from tdx_mcp.utils.help import get_price

@register_parser(0x547)
class QuotesEncrypt(BaseParser):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception('stocks count must > 0')
        self.body = bytearray(struct.pack('<H', count))
        
        for market, code in stocks:
            self.body.extend(struct.pack('<B6sHH', market.value, code.encode('gbk'), 22234, 2))

    @override
    def deserialize(self, data):
        data = bytes(b ^ 0x93 for b in data)
        
        count, = struct.unpack('<H', data[:2])
        pos = 2
        
        result = []
        for _ in range(count):
            market, code, active = struct.unpack('<B6sH', data[pos: pos + 9])
            pos += 9

            close, pos = get_price(data, pos)
            pre_close, pos = get_price(data, pos)
            open, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)

            time_raw, = struct.unpack('<I', data[pos: pos + 4])
            pos += 4

            u1, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            cur_vol, pos = get_price(data, pos)

            amount, = struct.unpack('<f', data[pos: pos + 4])
            pos += 4

            in_vol, pos = get_price(data, pos)
            out_vol, pos = get_price(data, pos)
            s_amount, pos = get_price(data, pos)
            open_amount, pos = get_price(data, pos)

            bids = []
            asks = []
            for _ in range(5):
                bid, pos = get_price(data, pos)
                ask, pos = get_price(data, pos)
                bid_vol, pos = get_price(data, pos)
                ask_vol, pos = get_price(data, pos)

                bid += close
                ask += close

                bids.append({
                    'price': bid,
                    'vol': bid_vol,
                })
                asks.append({
                    'price': ask,
                    'vol': ask_vol,
                })
                
            u2, u3, u4 = struct.unpack('<HII', data[pos: pos + 10])
            pos += 10

            # print(u1, u2, u3, u4)

            for _ in range(6):
                a, pos = get_price(data, pos)
                b, pos = get_price(data, pos)
                c, pos = get_price(data, pos)
                d, pos = get_price(data, pos)
                
            result.append({
                'market': MARKET(market),
                'code': code.decode('gbk'),
                'active': active,
                'close': close,
                'pre_close': close + pre_close,
                'open': close + open,
                'high': close + high,
                'low': close + low,
                'time': time(time_raw//10000, time_raw//100 % 100, time_raw % 100),
                'vol': vol,
                'cur_vol': cur_vol,
                'amount': amount,
                'in_vol': in_vol,
                'out_vol': out_vol,
                's_amount': s_amount,
                'open_amount': open_amount,
                'handicap': {
                    'bid': bids,
                    'ask': asks,
                },
            })
            
        return result