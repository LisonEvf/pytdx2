import struct
from typing import override

from const import MARKET
from parser.baseParser import BaseParser, register_parser
from utils.help import format_time, get_price


@register_parser(0x53e) # TODO: 
class QuotesDetail(BaseParser):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception('stocks count must > 0')
        self.body = bytearray(struct.pack('<H6sH', 5, b'', count))
        
        for market, code in stocks:
            self.body.extend(struct.pack('<B6s', market.value, code.encode('gbk')))

    @override
    def deserialize(self, data):
        _, count = struct.unpack('<HH', data[:4])
        pos = 4

        quotes = []
        for _ in range(count):
            market, code, active1 = struct.unpack('<B6sH', data[pos: pos + 9])
            pos += 9
            
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
            for _ in range(5): # 5个
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

            (unknown, _, rise_speed, active2) = struct.unpack('<h4shH', data[pos: pos + 10])
            pos += 10

            quotes.append({
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
                's_vol': s_vol,
                'b_vol': b_vol, # 外盘
                's_amount': s_amount,
                'open_amount': open_amount,# 开盘金额
                'handicap': {
                    'bid': bids,
                    'ask': asks,
                },
                'unknown': format(unknown, '016b'),
                'rise_speed': rise_speed, # 涨速
                'active1': active1,
                'active2': active2,
            })

        return quotes