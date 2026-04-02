import struct
from typing import override

from tdx_mcp.const import CATEGORY, FILTER_TYPE, MARKET, SORT_TYPE
from tdx_mcp.parser.baseParser import BaseParser, register_parser
from tdx_mcp.utils.help import format_time, get_price

@register_parser(0x54b) # TODO: 
class QuotesList(BaseParser):
    def __init__(self, category: CATEGORY, start: int = 0, count: int = 0x50, sortType: SORT_TYPE = SORT_TYPE.CODE, reverse: bool = False, filter: list[FILTER_TYPE] = []):
        sort_reverse = 0 if sortType == SORT_TYPE.CODE else 2 if reverse else 1

        filter_raw = 0
        for filter_type in filter:
            filter_raw &= filter_type.value

        self.body = struct.pack('<9H', category.value, sortType.value, start, count,  sort_reverse, 5, filter_raw, 1, 0)
    @override
    def deserialize(self, data):
        block, count = struct.unpack('<HH', data[:4])
        pos = 4

        stocks = []
        for _ in range(count):
            market, code, active1 = struct.unpack('<B6sH', data[pos: pos + 9])
            pos += 9
            price, pos = get_price(data, pos)
            pre_close, pos = get_price(data, pos)
            open, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)
            server_time, pos = get_price(data, pos)
            neg_price, pos = get_price(data, pos) # 盘后交易量
            vol, pos = get_price(data, pos)
            cur_vol, pos = get_price(data, pos)

            amount, = struct.unpack('<f', data[pos: pos + 4])
            pos += 4

            in_vol, pos = get_price(data, pos)
            out_vol, pos = get_price(data, pos)
            s_amount, pos = get_price(data, pos) #reversed_bytes2
            open_amount, pos = get_price(data, pos) #reversed_bytes3

            bids = []
            asks = []
            for _ in range(1):
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

            unknown, rise_speed, short_turnover, min2_amount, opening_rush, _, vol_rise_speed, depth, _, active2 = struct.unpack('<Hhhfh10sff24sH', data[pos: pos + 56])
            pos += 56

            stocks.append({
                'market': MARKET(market),
                'code': code.decode('gbk'),
                'close': price,
                'open': open + price,
                'high': high + price,
                'low': low + price,
                'pre_close': pre_close + price,
                'server_time': format_time(server_time),
                'neg_price': neg_price,
                'vol': vol,
                'cur_vol': cur_vol,
                'amount': amount,
                'in_vol': in_vol, # 内盘
                'out_vol': out_vol, # 外盘
                's_amount': s_amount,
                'open_amount': open_amount,
                'handicap': {
                    'bid': bids,
                    'ask': asks,
                },
                'unknown': format(unknown, '016b'),
                'rise_speed': rise_speed, # 涨速
                'short_turnover': short_turnover, # 短换手
                'min2_amount': min2_amount, # 2分钟金额
                'opening_rush': opening_rush, # 开盘抢筹
                'vol_rise_speed': vol_rise_speed, # 量涨速
                'depth': depth, # 委比
                'active': active1, # 活跃度
            })
        return stocks