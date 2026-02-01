from datetime import date
from utils.log import log
from const import CATEGORY, KLINE_TYPE, MARKET
from parser.baseparser import BaseParser, register_parser
import struct
from typing import override
import six
from utils.help import to_datetime, get_price, get_time, format_time

@register_parser(0x44e)
class Count(BaseParser):
    def __init__(self, market: MARKET):
        today = date.today().year * 10000 + date.today().month * 100 + date.today().day
        self.body = struct.pack(u'<HI', market.value, today)

    @override
    def deserialize(self, data):
        return struct.unpack('<H', data)[0]
        
@register_parser(0x44d) # TODO: 2Unknown
class List(BaseParser):
    def __init__(self, market: MARKET, start: int = 0, count: int = 1600):
        self.body = struct.pack(u'<H3I', market.value, start, count, 0)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        
        stocks = []
        for i in range(count):
            pos = 2 + i * 37
            (code, vol, name, _, unknown1, decimal_point, pre_close, unknown2, unknown3) = struct.unpack("<6sH8s8sfBfHH", data[pos: pos + 37])

            stocks.append({
                'code': code.decode('gbk', errors='ignore').rstrip('\x00'),
                'vol': vol,
                'name': name.decode('gbk', errors='ignore').rstrip('\x00'),
                'decimal_point': decimal_point,
                'pre_close': pre_close,
                'unknown1': [unknown1, unknown2, unknown3],
            })

        return stocks

@register_parser(0x450) # TODO: 2Unknown
class ListB(BaseParser):
    def __init__(self, market: MARKET, start):
        self.body = struct.pack(u'<HH', market.value, start)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])

        stocks = []
        for i in range(count):
            pos = 2 + i * 29
            (code, vol, name, unknown1, _, decimal_point, pre_close, unknown2, unknown3) = struct.unpack("<6sH8sHHBfHH", data[pos: pos + 29])

            stocks.append({
                'code': code.decode('gbk', errors='ignore').rstrip('\x00'),
                'vol': vol,
                'name': name.decode('gbk', errors='ignore').rstrip('\x00'),
                'decimal_point': decimal_point,
                'pre_close': pre_close,
                'unknown1': [unknown1, unknown2, unknown3],
            })

        return stocks

@register_parser(0x51d) # TODO: 未完成
class IndexInfo(BaseParser): 
    def __init__(self, market: MARKET, code: str):
        if type(code) is six.text_type:
            code = code.encode("gbk")
        self.body = struct.pack(u'<H6sI', market.value, code, 0)

    @override
    def deserialize(self, data):
        (count, market, code, active) = struct.unpack('<IB6sH', data[:13])
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

        print(code.decode('utf-8'),format_time(maybe_server_time), "{:2}".format(maybe_after_hour), "{:8}".format(maybe_cur_vol), '|',"{:9}".format(a), "{:9}".format(b), "{:9}".format(open_amount), "{:7}".format(d), "{:9}".format(e), "{:9}".format(f), '|', g, h, i, j, k, l, m, n, o, p)
        
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
            'code': code.decode('utf-8'),
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
    
@register_parser(0x523)
class K_Line(BaseParser):
    def __init__(self, market: MARKET, code: str, kline_type: KLINE_TYPE, start: int = 0, count: int = 800):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<H6sHHHH10s', market.value, code, kline_type.value, 1, start, count, b'')
        
        self.kline_type = kline_type
        
    @override
    def deserialize(self, data):
        data_len = len(data)
        count, = struct.unpack('<H', data[:2])
        pos = 2

        minute_category = self.kline_type.value < 4 or self.kline_type.value == 7 or self.kline_type.value == 8

        bars = []
        for i in range(count):
            date, = struct.unpack("<I", data[pos: pos + 4])
            pos += 4
            datetime = to_datetime(date, minute_category)
            
            open, pos = get_price(data, pos)
            close, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)
            
            vol, amount = struct.unpack("<ff", data[pos: pos + 8])
            pos += 8

            upCount = 0
            downCount = 0
            if pos < data_len:
                try:
                    try_date, = struct.unpack("<I", data[pos: pos + 4])
                    try_date_time = to_datetime(try_date, minute_category)
                    if try_date_time.year < datetime.year:
                        raise ValueError()
                except ValueError:
                    upCount, downCount = struct.unpack("<HH", data[pos: pos + 4])
                    pos += 4
            
            bar = {
                'datetime': datetime,
                'open': open,
                'close': close,
                'high': high,
                'low': low,
                'vol': vol,
                'amount': amount,
            }
            if upCount != 0 or downCount != 0:
                bar['upCount'] = upCount
                bar['downCount'] = downCount
            bars.append(bar)
            
        return bars

@register_parser(0x52d)
class K_Line_Offset(K_Line):
    pass

@register_parser(0x537)
class IndexChart(BaseParser):
    def __init__(self, market: MARKET, code: str, start: int = 0, count: int = 0xba00):
        if type(code) is six.text_type:
            code = code.encode("gbk")
        self.body = bytearray(struct.pack('<H6sHH', market.value, code, start, count))
        
    @override
    def deserialize(self, data):
        num, _ = struct.unpack('<HH', data[:4])

        result = []
        pos = 4
        start_price = 0
        start_fast = 0
        for _ in range(num):
            price, pos = get_price(data, pos)
            fast, pos = get_price(data, pos)
            amount, pos = get_price(data, pos)

            result.append({
                'price': start_price + price,
                'fast': start_fast + fast,
                'amount': amount,
            })
            if start_price == 0:
                start_price = price
            if start_fast == 0:
                start_fast = fast
        return result
        

@register_parser(0x53e) # TODO: 
class QuotesDetail(BaseParser):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception("stocks count must > 0")
        self.body = bytearray(struct.pack('<H6sH', 5, b'', count))
        
        for stock in stocks:
            (market, code) = stock
            if type(code) is six.text_type:
                code = code.encode("utf-8")
            self.body.extend(struct.pack('<B6s', market.value, code))

    @override
    def deserialize(self, data):
        (_, count) = struct.unpack('<HH', data[:4])
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
                'code': code.decode('utf-8'),
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


@register_parser(0x53f)
class TopStocksBoard(BaseParser):
    def __init__(self, category: CATEGORY, size: int = 20):
        self.body = struct.pack('<BB7sB', category.value, 5, bytes.fromhex('000000000100'), size)
    @override
    def deserialize(self, data):
        size, = struct.unpack('<B', data[:1])
        pos = 1

        result = {
            'increase': [],
            'decrease': [],
            'amplitude': [],
            'rise_speed': [],
            'fall_speed': [],
            'vol_ratio': [],
            'pos_commission_ratio': [],
            'neg_commission_ratio': [],
            'turnover': [],
        }

        for item in result:
            for _ in range(size):
                market, code, price, value = struct.unpack('<B6sff', data[pos: pos + 15])
                pos += 15

                result[item].append({
                    'market': MARKET(market),
                    'code': code.decode('utf-8'),
                    'price': price,
                    'value': value,
                })
         
        return result

# >0700
# 01 393939393939 c437 0200 # 01 393939393939 e355 0200
# 00 333939303031 c437 0200 # 00 333939303031 ae55 0200
# 02 383939303530 bf37 0200 # 02 383939303530 aa55 0200
# 00 333939303036 c437 0200 # 00 333939303036 554a 0200
# 01 303030363838 c437 0200 # 01 303030363838 f949 0200
# 01 303030333030 c437 0200 # 01 303030333030 f949 0200
# 01 383830303035 c337 0200 # 01 383830303035 b055 0200

# < 9493
# 92aaaaaaaaaaaa
# 1f812b7bbc50b941891a97478970c69193d9233a48619093b572a4c0054d18669229585c6e9213365ad20c7a4e900d5a3a8d9334800f9c0c7701973b5a91bd953a083e7d9293089d289c939393939393939391939393939393939393
# 6b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc9393
# 
# 93a0aaaaa3a3a2
# 1e810a733192603f917e3492308a7e34923dc69193b01c6a317c97938830eac0151721249139666324912b6f6afd1f005c9f3f02329e930c8a1881077f7f9793a8910d5c048e933e83399c93939393939393939193900ae39293939393
# 4a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a7331929393
# 
# 91abaaaaa3a6a3
# 9b98334b824b962d92299e429e3ac691932692222b429a93af160bc3311a6c972e2d419713224f923c6f239293930791179193939293939334912592939393939393939391939393939393939393
# 734b82734b829393734b82734b829393734b82734b829393734b82734b829393734b82734b829393734b82734b829393
# 
# 93a0aaaaa3a3a5
# 1e810d68b56cff63a8009a63a860da9193b42b29733c921c1957aa6ff270c103382ac4251c34cb2b535dba3c796c919393009f3e9b939395929393069a199b939393939393939391935d48c29393939393
# 4d68b54d68b593934d68b54d68b593934d68b54d68b593934d68b54d68b593934d68b54d68b593934c68b54c68b59393
# 
# 92a3a3a3a5abab
# 188106358379ba55b2329755b26ada9193903d7841942d1cfac7fbdec2247004821e0e49821f4f6692013f329293932296049093939293939316971797939393939393939391939393939393939393
# 463583463583939346358346358393934635834635839393463583463583939346358346358393934635834635839393
# 
# 92a3a3a3a0a3a3
# 1f813936ab6bd048b63a9548b66ada919354922b285f0e920b421192e12943c1271614a0290840a6176235b2240c229793930691189193939193939314923592939393939393939391939393939393939393
# 7936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab9393
# 
# 92ababa3a3a3a6
# d5803325b74718904f709b2b0c8d6716b13ec6919393355001789b030097498e48c037923897230f0e21923b2d0791939307b628b3939338973792939313918e93933a918e93933a929b91939393939393939393
# 7325b77325b793937325b77325b793937325b77325b793937325b77325b793937325b77325b793937325b77325b79393

# 93 -> 0  -> a3
# 92 -> 1  -> a2
# 91 -> 2  -> a1
# 90 -> 3  -> a0
# 97 -> 4  -> a7
# 96 -> 5  -> a6
# 95 -> 6  -> a5
# 94 -> 7  -> a4
# 9b -> 8  -> ab
# 9a -> 9  -> aa
# 99 -> 10
# 98 -> 11
# 9f -> 12
# 9e -> 13
# 9d -> 14
# 9c -> 15
# 83 -> 16
# 82 -> 17
# 81 -> 18
@register_parser(0x547) # TODO: 怪异编码
class TODO547(BaseParser):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception("stocks count must > 0")
        self.body = bytearray(struct.pack('<H', count))
        
        for (market, code) in stocks:
            if type(code) is six.text_type:
                code = code.encode("gbk")
            self.body.extend(struct.pack('<B6sI', market.value, code, 0))
        print("body: ", self.body.hex())
        # self.body = bytearray.fromhex('070001393939393939c437020000333939303031c437020002383939303530bf37020000333939303036c437020001303030363838c437020001303030333030c437020001383830303035c3370200')
    @override
    def deserialize(self, data):
        print(struct.unpack('<H', data[:2]))
        # print("data: ", data.hex())
            
        return data

@register_parser(0x54b) # TODO: 
class QuotesList(BaseParser):
    def __init__(self, category: CATEGORY, start: int = 0, count: int = 0x50):
        self.body = struct.pack('<9H', category.value, 0, start, count, 0 ,5, 0, 1, 0)
    @override
    def deserialize(self, data):
        block, count = struct.unpack('<HH', data[:4])
        pos = 4

        stocks = []
        for _ in range(count):
            (market, code, active1 ) = struct.unpack('<B6sH', data[pos: pos + 9])
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

            s_vol, pos = get_price(data, pos)
            b_vol, pos = get_price(data, pos)
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
                'unknown': format(unknown, '016b'),
                'rise_speed': rise_speed, # 涨速
                'short_turnover': short_turnover, # 短换手
                'min2_amount': min2_amount, # 2分钟金额
                'opening_rush': opening_rush, # 开盘抢筹
                'vol_rise_speed': vol_rise_speed, # 量涨速
                'depth': depth, # 委比
                'active1': active1, # 活跃度
                'active2': active2, # 活跃度
            })
        return stocks

@register_parser(0x54c)
class Quotes(QuotesList):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception("stocks count must > 0")
        self.body = bytearray(struct.pack('<H6sH', 5, b'', count))
        for market, code in stocks:
            self.body.extend(struct.pack('<B6s', market.value, code.encode('gbk')))


@register_parser(0x563)
class Unusual(BaseParser): # 主力监控
    def __init__(self, market: MARKET, start: int, count: int = 600):
        self.body = struct.pack('<HII', market.value, start, count)
    @override
    def deserialize(self, data):
        def unpack_by_type(type: int, data: bytearray):
            v1, v2, v3, v4 = struct.unpack('<B3f', data)
            desc = ''
            val = ''
            if type == 0x03: 
                desc = f"主力{"买入" if v1 == 0x00 else "卖出"}" 
                val = f"{v2:.2f}/{v3:.2f}"
            elif type == 0x04: 
                desc = "加速拉升"
                val = f"{v2*100:.2f}%"
            elif type == 0x05: 
                desc = "加速下跌"
            elif type == 0x06:
                desc = "低位反弹"
                val = f"{v2*100:.2f}%"
            elif type == 0x07: 
                desc = "高位回落"
                val = f"{v2*100:.2f}%"
            elif type == 0x08: 
                desc = "撑杆跳高"
                val = f"{v2*100:.2f}%"
            elif type == 0x09: 
                desc = "平台跳水"
                val = f"{v2*100:.2f}%"
            elif type == 0x0a: 
                desc = "单笔冲" + ("跌" if v2 < 0x00 else "涨")
                val = f"{v2*100:.2f}%"
            elif type == 0x0b:
                desc = f"区间放量{"平" if v3 == 0 else "跌" if v3 < 0 else "涨"}"
                val = f"{v2:.1f}倍{"" if v3 == 0 else f"{v3*100:.2f}%"}"
            elif type == 0x0c: 
                desc = "区间缩量"
            elif type == 0x10: 
                desc = "大单托盘"
                val = f"{v4:.2f}/{v3:.2f}"
            elif type == 0x11: 
                desc = "大单压盘"
                val = f"{v2:.2f}/{v3:.2f}"
            elif type == 0x12: 
                desc = "大单锁盘"
            elif type == 0x13: 
                desc = "竞价试买"
                val = f"{v2:.2f}/{v3:.2f}"
            elif type == 0x14: 
                sub_type, v2, v3 = struct.unpack('<Bff', data[1:10])
                direction = "涨" if v1 == 0x00 else "跌"
                if sub_type == 0x01:
                    desc = f"逼近{direction}停"
                elif sub_type == 0x02:
                    desc = f"封{direction}停板"
                elif sub_type == 0x04:
                    desc = f"封{direction}大减"
                elif sub_type == 0x05:
                    desc = f"打开{direction}停"
                val = f"{v2:.2f}/{v3:.2f}"
            elif type == 0x15:
                if v1 == 0x00:
                    desc = "尾盘??"
                elif v1 == 0x01:
                    desc = "尾盘对倒"
                elif v1 == 0x02:
                    desc = "尾盘拉升"
                else:
                    desc = "尾盘打压"
                val = f"{v2*100:.2f}%/{v3:.2f}"
            elif type == 0x16:
                desc = f"盘中{"弱" if v2 < 0x00 else "强"}势"
                val = f"{v2*100:.2f}%"
            elif type == 0x1d:
                desc = "急速拉升"
                val = f"{v2*100:.2f}%"
            elif type == 0x1e:
                desc = "急速下跌" 
                val = f"{v2*100:.2f}%"
            return desc, val
        (count, ) = struct.unpack('<H', data[:2])

        stocks = []
        for i in range(count):
            pice_data = data[32 * i + 2: 32 * (i + 1) + 2]

            market, code, _, type, _, index, z = struct.unpack('<H6sBBBHH', pice_data[:15])
            hour, minute_sec = struct.unpack('<BH', pice_data[29: 32])

            desc, value = unpack_by_type(type, pice_data[15: 28])

            stocks.append({
                "index": index,
                "market": MARKET(market),
                "code": code.decode('gbk').replace('\x00', ''),
                "time": f"{hour:02d}:{minute_sec // 100:02d}:{minute_sec % 100:02d}",
                "desc": desc,
                "value": value,
            })
        return stocks
    
    

@register_parser(0xfb4)
class HistoryOrders(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IB6s', date, market.value, code)

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
        return {
            'pre_close': pre_close,
            'orders': orders,
        }

@register_parser(0xfb5)
class HistoryTransaction(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date, start: int, count: int):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IH6sHH', date, market.value, code, start, count)

    @override
    def deserialize(self, data):
        count, _ = struct.unpack('<H4s', data[:6])
        pos = 6

        last_price = 0
        transactions = []
        for _ in range(count):
            hour, minute, pos = get_time(data, pos)

            price, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            buyorsell, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)

            last_price += price
            transactions.append({
                "time": "%02d:%02d" % (hour, minute),
                'price': last_price,
                'vol': vol,
                'action': 'SELL' if buyorsell == 1 else 'BUY' if buyorsell == 0 else 'NEUTRAL',
                'unknown': unknown,
            })

        return transactions

@register_parser(0xfc5)
class Transaction(BaseParser):
    def __init__(self, market: MARKET, code: str, start: int, count: int):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<H6sHH', market.value, code, start, count)

    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])
        pos = 2

        last_price = 0
        transactions = []
        for _ in range(count):
            hour, minute, pos = get_time(data, pos)

            price, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            trans, pos = get_price(data, pos)
            buyorsell, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)

            last_price += price
            transactions.append({
                "time": "%02d:%02d" % (hour, minute),
                'price': last_price,
                'vol': vol,
                'trans': trans,
                'action': 'SELL' if buyorsell == 1 else 'BUY' if buyorsell == 0 else 'NEUTRAL',
                'unknown': unknown,
            })

        return transactions

@register_parser(0xfd1)
class ChartSampling(BaseParser):
    def __init__(self, market: MARKET, code: str):
        if type(code) is six.text_type:
            code = code.encode("gbk")
        self.body = bytearray(struct.pack('<H6s', market.value, code))
        
        self.body.extend(bytearray().fromhex('0000000000000000000000000000000001001400000000010000000000'))
    @override
    def deserialize(self, data):
        market, code = struct.unpack('<H6s', data[:8])
        num, pre_close, _ = struct.unpack('<HfH', data[34:42])

        prices = []
        for i in range(num):
            p, = struct.unpack('<f', data[42 + i * 4: 42 + (i + 1) * 4])
            prices.append(p)
            
        return {
            'market': market,
            'code': code.decode('gbk'),
            'pre_close': pre_close,
            'prices': prices
        }