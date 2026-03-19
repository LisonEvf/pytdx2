import struct
from typing import override

from const import MARKET
from parser.base_parser import BaseParser, register_parser
from utils.help import format_time, get_price


@register_parser(0x51a)
class VolumeProfile(BaseParser):
    def __init__(self, market: MARKET, code: str):
        self.body = struct.pack(u'<H6s', market.value, code.encode('gbk'))
    
    @override
    def deserialize(self, data):
        count, market, code, active = struct.unpack('<HB6sH', data[:11])
        pos = 11

        price, pos = get_price(data, pos)
        pre_close, pos = get_price(data, pos)
        open, pos = get_price(data, pos)
        high, pos = get_price(data, pos)
        low, pos = get_price(data, pos)
        server_time, pos = get_price(data, pos)
        neg_price, pos = get_price(data, pos)
        vol, pos = get_price(data, pos)
        cur_vol, pos = get_price(data, pos)

        amount, = struct.unpack('<f', data[pos: pos + 4])
        pos += 4

        s_vol, pos = get_price(data, pos)
        b_vol, pos = get_price(data, pos)
        s_amount, pos = get_price(data, pos)
        open_amount, pos = get_price(data, pos) 

        bids = []
        asks = []
        for _ in range(3):
            bid, pos = get_price(data, pos)
            ask, pos = get_price(data, pos)
            bid_vol, pos = get_price(data, pos)
            ask_vol, pos = get_price(data, pos)

            bid += price
            ask += price

            bids.append({
                'price': bid,
                'vol': bid_vol,
            })
            asks.append({
                'price': ask,
                'vol': ask_vol,
            })

        # 没明白是什么值
        unknown, = struct.unpack('<H', data[pos: pos + 2])
        pos += 2
        print(unknown)
        
        vol_profile = []
        start_price = 0
        for _ in range(count):
            price, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            buy, pos = get_price(data, pos)
            sell, pos = get_price(data, pos)
            
            start_price += price
            vol_profile.append({
                'price': start_price,
                'vol': vol,
                'buy': buy,
                'sell': sell
            })
        
        return {
            'market': MARKET(market),
            'code': code.decode('gbk'),
            'price': price,
            'open': open + price,
            'high': high + price,
            'low': low + price,
            'pre_close': pre_close + price,
            'server_time': format_time(server_time),
            'neg_price': neg_price,
            'vol': vol,
            'cur_vol': cur_vol,
            'amount': amount,
            's_vol': s_vol, # 内盘
            'b_vol': b_vol, # 外盘
            's_amount': s_amount,
            'open_amount': open_amount,
            'handicap': {
                'bid': bids,
                'ask': asks,
            },
            'active': active,
            'vol_profile': vol_profile
        }