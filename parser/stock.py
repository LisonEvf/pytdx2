from datetime import date
from utils.log import log
from const import CATEGORY, KLINE_TYPE, MARKET
from parser.baseparser import BaseParser, register_parser
import struct
from typing import override
import six
from utils.help import to_datetime, get_price, get_time, format_time


@register_parser(0x523)
class K_Line(BaseParser):
    def __init__(self, market: MARKET, code: str, kline_type: KLINE_TYPE, start: int = 0, count: int = 800):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<H6sHHHH10s', market.value, code, kline_type.value, 1, start, count, b'')
        
        self.kline_type = kline_type
        
    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        pos = 2

        minute_category = self.kline_type.value < 4 or self.kline_type.value == 7 or self.kline_type.value == 8

        bars = []
        for i in range(count):
            (date,) = struct.unpack("<I", data[pos: pos + 4])
            pos += 4
            datetime = to_datetime(date, minute_category)
            
            open, pos = get_price(data, pos)
            close, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)
            
            (vol, amount) = struct.unpack("<ff", data[pos: pos + 8])
            pos += 8

            upCount = 0
            downCount = 0
            if i < count - 1:
                try:
                    try_date = to_datetime(struct.unpack("<I", data[pos: pos + 4])[0], minute_category)
                    if len(bars) > 0 and try_date.year < bars[-1]['datetime'].year:
                        raise ValueError()
                except ValueError:
                    (upCount, downCount) = struct.unpack("<HH", data[pos: pos + 4])
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

@register_parser(0x44e)
class Count(BaseParser):
    def __init__(self, market: MARKET):
        today = date.today().year * 10000 + date.today().month * 100 + date.today().day
        self.body = struct.pack(u'<HI', market.value, today)

    @override
    def deserialize(self, data):
        return {
            'count': struct.unpack('<H', data[:2])[0]
        }
        
@register_parser(0x44d) # TODO: 2Unknown
class List(BaseParser):
    def __init__(self, market: MARKET, start: int = 0, count: int = 1600):
        self.body = struct.pack(u'<HIII', market.value, start, count, 0)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        
        stocks = []
        for i in range(count):
            pos = 2 + i * 37
            (code, vol, name, _, unknown1, decimal_point, pre_close, unknown2, unknown3) = struct.unpack("<6sH8s8s4sBfHH", data[pos: pos + 37])
            code = code.decode('gbk', errors='ignore').rstrip('\x00')
            name = name.decode('gbk', errors='ignore').rstrip('\x00')

            # print(data[pos: pos + 37].hex())
            stocks.append({
                'code': code,
                'vol': vol,
                'name': name,
                'decimal_point': decimal_point,
                'pre_close': pre_close,
                'unknown1': [unknown1.hex(), unknown2, unknown3],
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
            (code, vol, name, unknown1, decimal_point, pre_close, unknown2) = struct.unpack("<6sH8s4sBfI", data[pos: pos + 29])
            code = code.decode('gbk', errors='ignore').rstrip('\x00')
            name = name.decode('gbk', errors='ignore').rstrip('\x00')
            
            stocks.append({
                'code': code,
                'vol': vol,
                'name': name,
                'decimal_point': decimal_point,
                'pre_close': pre_close,
                'unknown1': [unknown1.hex(), unknown2],
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

        point, pos = get_price(data, pos)
        last_diff, pos = get_price(data, pos)
        start_diff, pos = get_price(data, pos)
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

        print(format_time(maybe_server_time), maybe_after_hour, maybe_cur_vol)
        print(a, b, open_amount, d, e, f, '|', g, h, i, j, k, l, m, n, o, p)
        
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
            'market': market,
            'code': code,
            'active': active,
            'point': point,
            'last_diff': last_diff,
            'start_diff': start_diff,
            'high_diff': high_diff,
            'low_diff': low_diff,
            'vol': vol,
            'amount': amount,
            'up_count': up_count,
            'down_count': down_count
        }

@register_parser(0xfb4)
class HistoryOrders(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IB6s', date, market.value, code)

    @override
    def deserialize(self, data):
        count, unknown = struct.unpack('<HI', data[:6])
        pos = 2

        orders = []
        last_price = 0
        for _ in range(count):
            price, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)

            last_price += price

            orders.append({
                'price': last_price,
                'unknown': unknown,
                'vol': vol,
            })

        return orders

@register_parser(0xfb5)
class HistoryTransaction(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date, start: int, count: int):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IH6sHH', date, market.value, code, start, count)

    @override
    def deserialize(self, data):
        (count, _) = struct.unpack('<H4s', data[:6])
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
                'action': 'SELL' if buyorsell == 1 else 'BUY',
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
                'action': 'SELL' if buyorsell == 1 else 'BUY',
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
        num, price, _ = struct.unpack('<HfH', data[34:42])

        print(num)
        prices = []
        for i in range(num):
            p, = struct.unpack('<f', data[42 + i * 4: 42 + (i + 1) * 4])
            prices.append(p)
            
        return {
            'market': market,
            'code': code.decode('gbk'),
            'price': price,
            'prices': prices
        }


@register_parser(0x537)
class IndexChartSampling(BaseParser):
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
        for i in range(num):
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
        

@register_parser(0x53e)
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
            (market, code, active1) = struct.unpack('<B6sH', data[pos: pos + 9])
            pos += 9
            code = code.decode('utf-8')
            
            price, pos = get_price(data, pos)
            last_close, pos = get_price(data, pos)
            open, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)
            server_time, pos = get_price(data, pos)
            after_hour, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            cur_vol, pos = get_price(data, pos)
            
            last_close += price
            open += price
            high += price
            low += price
            server_time = format_time(server_time)

            (amount,) = struct.unpack('<f', data[pos: pos + 4])
            pos += 4

            s_vol, pos = get_price(data, pos)
            b_vol, pos = get_price(data, pos)
            s_amount, pos = get_price(data, pos) #reversed_bytes2
            b_amount, pos = get_price(data, pos) #reversed_bytes3

            handi_cap = {
                'bid': [],
                'ask': [],
            }
            for _ in range(5): # 5个
                bid, pos = get_price(data, pos)
                ask, pos = get_price(data, pos)
                bid_vol, pos = get_price(data, pos)
                ask_vol, pos = get_price(data, pos)

                bid += price
                ask += price

                handi_cap['bid'].append({
                    'price': bid,
                    'vol': bid_vol,
                })
                handi_cap['ask'].append({
                    'price': ask,
                    'vol': ask_vol,
                })

            (v1, unknown, rise_speed, active2) = struct.unpack('<h4shH', data[pos: pos + 10])
            pos += 10

            quotes.append({
                'market': MARKET(market),
                'code': code,
                'price': price,
                'open': open,
                'high': high,
                'low': low,
                'last_close': last_close,
                'server_time': server_time,
                'after_hour': after_hour,
                'vol': vol,
                'cur_vol': cur_vol,
                'amount': amount,
                's_vol': s_vol,
                'b_vol': b_vol,
                's_amount': s_amount,
                'b_amount': b_amount,# 开盘金额
                'handi_cap': handi_cap,
                'v1': format(v1, '016b'),
                'unknown': unknown.hex(),
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
        # count = len(stocks)
        # if count <= 0:
        #     raise Exception("stocks count must > 0")
        # self.body = bytearray(struct.pack('<H', count))
        
        # for (market, code) in stocks:
        #     if type(code) is six.text_type:
        #         code = code.encode("gbk")
        #     self.body.extend(struct.pack('<B6sI', market.value, code, 0))
        self.body = bytearray.fromhex('070001393939393939c437020000333939303031c437020002383939303530bf37020000333939303036c437020001303030363838c437020001303030333030c437020001383830303035c3370200')
    @override
    def deserialize(self, data):
        print("data: ", data.hex())
            
        return data

@register_parser(0x54b)
class QuotesList(BaseParser):
    def __init__(self, category: CATEGORY, start: int = 0, count: int = 0x50):
        self.body = struct.pack('<HHHHHHHHH', category.value, 0, start, count, 0 ,5, 0, 1, 0)
    @override
    def deserialize(self, data):
        (block, count) = struct.unpack('<HH', data[:4])
        pos = 4

        stocks = []
        for _ in range(count):
            (market, code, active1 ) = struct.unpack('<B6sH', data[pos: pos + 9])
            pos += 9
            price, pos = get_price(data, pos)
            last_close, pos = get_price(data, pos)
            open, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)
            server_time, pos = get_price(data, pos)
            after_hour, pos = get_price(data, pos) # 盘后交易量
            vol, pos = get_price(data, pos)
            cur_vol, pos = get_price(data, pos)

            last_close += price
            open += price
            high += price
            low += price
            server_time = format_time(server_time)

            (amount,) = struct.unpack('<f', data[pos: pos + 4])
            pos += 4

            s_vol, pos = get_price(data, pos)
            b_vol, pos = get_price(data, pos)
            s_amount, pos = get_price(data, pos) #reversed_bytes2
            b_amount, pos = get_price(data, pos) #reversed_bytes3

            handi_cap = {
                'bid': [],
                'ask': [],
            }
            for _ in range(1): # 5个
                bid, pos = get_price(data, pos)
                ask, pos = get_price(data, pos)
                bid_vol, pos = get_price(data, pos)
                ask_vol, pos = get_price(data, pos)

                bid += price
                ask += price

                handi_cap['bid'].append({
                    'price': bid,
                    'vol': bid_vol,
                })
                handi_cap['ask'].append({
                    'price': ask,
                    'vol': ask_vol,
                })

            (unknown, rise_speed, short_turnover, twomin_amount, opening_rush, _, vol_rise_speed, depth, _, active2) = struct.unpack('<Hhhfh10sff24sH', data[pos: pos + 56])
            pos += 56

            stocks.append({
                'market': MARKET(market),
                'code': code.decode('gbk'),
                'price': price,
                'open': open,
                'high': high,
                'low': low,
                'last_close': last_close,
                'server_time': server_time,
                'after_hour': after_hour,
                'vol': vol,
                'cur_vol': cur_vol,
                'amount': amount,
                's_vol': s_vol,
                'b_vol': b_vol,
                's_amount': s_amount,
                'b_amount': b_amount,
                'handi_cap': handi_cap,
                'unknown': format(unknown, '016b'),
                'rise_speed': rise_speed, # 涨速
                'short_turnover': short_turnover, # 短换手
                'twomin_amount': twomin_amount, # 2分钟金额
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
        self.body = bytearray(struct.pack('<HIHH', 5, 0, 0, count))
        for (market, code) in stocks:
            self.body.extend(struct.pack('<B6s', market.value, code.encode('gbk')))


@register_parser(0x563)
class Unusual(BaseParser): # 主力监控
    def __init__(self, market: MARKET, start: int, count: int = 600):
        self.body = struct.pack('<HII', market.value, start, count)
    @override
    def deserialize(self, data):
        (count, ) = struct.unpack('<H', data[:2])

        stocks = []
        for i in range(count):
            pice_data = data[32 * i + 2: 32 * (i + 1) + 2]

            market, code, _, type, _, index, z = struct.unpack('<H6sBBBHH', pice_data[:15])
            hour, minute_sec = struct.unpack('<BH', pice_data[29: 32])

            type, val = self.unpack_by_type(type, pice_data[15: 28])

            # print(pice_data.hex())
            stocks.append({
                "index": index,
                "market": MARKET(market),
                "code": code.decode('gbk').replace('\x00', ''),
                "time": f"{hour:02d}:{minute_sec // 100:02d}:{minute_sec % 100:02d}",
                "type": type,
                "val": val,
            })
        return stocks
    
    def unpack_by_type(self, type: int, data: bytearray):
        v1, v2, v3, v4 = struct.unpack('<Bfff', data)
        desc = ''
        val = ''
        match type:
            case 0x03: # 主力买入、卖出
                if v1 == 0x00:
                    desc = "主力买入"
                else:
                    desc = "主力卖出"
                val = f"{v2:.2f}/{v3:.2f}"
            case 0x04: # 加速拉升
                desc = "加速拉升"
                val = f"{v2*100:.2f}%"
            case 0x05: # 加速下跌
                desc = "加速下跌"
            case 0x06: # 低位反弹
                desc = "低位反弹"
                val = f"{v2*100:.2f}%"
            case 0x07: # 高位回落
                desc = "高位回落"
                val = f"{v2*100:.2f}%"
            case 0x08: # 撑杆跳高
                desc = "撑杆跳高"
                val = f"{v2*100:.2f}%"
            case 0x09: # 平台跳水
                desc = "平台跳水"
                val = f"{v2*100:.2f}%"
            case 0x0a: # 单笔冲涨、跌
                desc = "单笔冲" + ("跌" if v2 < 0x00 else "涨")
                val = f"{v2*100:.2f}%"
            case 0x0b: # 区间放量 涨、跌、平
                desc = "区间放量"
                val = f"{v2:.1f}倍"
                if v3 == 0:
                    desc += "平"
                else:
                    desc += "跌" if v3 < 0 else "涨"
                    val += f"{v3*100:.2f}%"
            case 0x0c: # 区间缩量
                desc = "区间缩量"
            case 0x10: # 大单托盘
                desc = "大单托盘"
                val = f"{v4:.2f}/{v3:.2f}"
            case 0x11: # 大单压盘
                desc = "大单压盘"
                val = f"{v2:.2f}/{v3:.2f}"
            case 0x12: # 大单锁盘
                desc = "大单锁盘"
            case 0x13: # 竞价试买
                desc = "竞价试买"
                val = f"{v2:.2f}/{v3:.2f}"
            case 0x14: # 打开涨停
                type, v2, v3 = struct.unpack('<Bff', data[1:10])
                direction = "涨" if v1 == 0x00 else "跌"
                if type == 0x01:
                    desc = f"逼近{direction}停"
                elif type == 0x02:
                    desc = f"封{direction}停板"
                elif type == 0x04:
                    desc = f"封{direction}大减"
                elif type == 0x05:
                    desc = f"打开{direction}停"
                val = f"{v2:.2f}/{v3:.2f}"
            case 0x15: # 尾盘
                if v1 == 0x00:
                    desc = "尾盘??"
                elif v1 == 0x01:
                    desc = "尾盘对倒"
                elif v1 == 0x02:
                    desc = "尾盘拉升"
                else:
                    desc = "尾盘???"
                val = f"{v2*100:.2f}%/{v3:.2f}"
            case 0x16: # 盘中弱势、强势
                desc = "盘中" + ("弱势" if v2 < 0x00 else "强势")
                val = f"{v2*100:.2f}%"
            case 0x1d: # 急速拉升
                desc = "急速拉升"
                val = f"{v2*100:.2f}%"
            case 0x1e: # 急速下跌
                desc = "急速下跌" 
                val = f"{v2*100:.2f}%"
            
        return desc, val

@register_parser(0x6b9) # TODO: 有点没用
class TODO6b9(BaseParser):
    def __init__(self):
        self.body = bytearray(struct.pack('<II', 0, 30000))
        path = "iwshop/{0}_{1}.htm".format(1, 605598)
        self.body.extend(struct.pack('<19s281s', path.encode('gbk'), b''))
        
    @override
    def deserialize(self, data):
        print(data[4:].decode('utf-8'))
        return data
      