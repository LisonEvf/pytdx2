from datetime import date, time

from const import BOARD_TYPE, EX_CATEGORY, EX_MARKET, PERIOD, MARKET
from parser.baseparser import BaseParser, register_parser
import struct
from typing import override

from parser.quotation import file
from utils.help import to_datetime

@register_parser(0x23f0, 1)
class Count(BaseParser): # ?
    @override
    def deserialize(self, data):
        id, _, _, count, _, _ = struct.unpack('<11s5I', data[:31])
        return count
    
@register_parser(0x23f4, 1)
class CategoryList(BaseParser):
    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])

        result = []
        for i in range(count):
            market, name, code, abbr = struct.unpack('<B32sB30s', data[64 * i + 2: 64 * i + 66])
            result.append({
                'market': EX_MARKET(market),
                'name': name.decode('gbk').replace('\x00', ''),
                'code': code,
                'abbr': abbr.decode('gbk').replace('\x00', '')
            })
        return result
    
@register_parser(0x23f5, 1)
class Detail(BaseParser):
    def __init__(self, start, count):
        self.body = struct.pack('<IH', start, count)

    @override
    def deserialize(self, data):
        start, count = struct.unpack('<IH', data[:6])
        
        instruments = []
        for i in range(count):
            market, category, u3, u4, code, name, u5, u6, u7, u8, u9, u10, u11, u12, u13, u14 = struct.unpack('<BBBH9s26sffHHHHHHHH', data[i * 64 + 6: i * 64 + 70])

            instruments.append({
                'market': market,
                'category': category,
                'code': code.decode('gbk').replace('\x00', ''),
                'desc': [u3, u4, u5, u6, u7, u8, u9, u10, u11, u12, u13, u14],
                'name': name.decode('gbk', errors='ignore').replace('\x00', ''),
            })
        
        return instruments

@register_parser(0x23f6, 1)
class f23f6(BaseParser):
    def __init__(self):
        self.body = struct.pack('<HHH', 0, 0, 500)

    @override
    def deserialize(self, data):
        start, count = struct.unpack('<IH', data[:6])

        result = []
        for i in range(count):
            z = struct.unpack('<B8sB12H', data[i * 34 + 6: i * 34 + 40])
            print(z)

        return None

def unpack_futures(data, code_len: int = 23):
    if len(data) == 292 + code_len:
        raise Exception('')
    category, code = struct.unpack(f'<B{code_len}s', data[:1 + code_len])
    active, pre_close, open, high, low, current, open_position, add_position, vol, curr_vol, amount, in_vol, ex_vol, u14, hold_position = struct.unpack(f'<I5f4If4I', data[1 + code_len: 61 + code_len])
    pending_list = struct.unpack('<5f5I5f5I', data[61 + code_len: 141 + code_len])
    pending = {
        'bids': [{'price': pending_list[i], 'vol': pending_list[i + 5]} for i in range(5)],
        'asks': [{'price': pending_list[i], 'vol': pending_list[i + 5]} for i in range(10, 15)]
    }
    u1, settlement_price, u2, average_price, pre_settlement_price, u3, u4, u5, u6, pre_close_price  = struct.unpack('<HfIffIIIIf', data[141 + code_len: 179 + code_len])
    s1, pre_vol, u7, s2, u8, day3_raise, s3, settlement_price2, date_raw, u9, raise_speed, u10, s4, u11, u12 = struct.unpack('<12sff12sff25sfIIff24sHB', data[179 + code_len: 291 + code_len])

    return {
            'category': EX_CATEGORY(category), 
            'code': code.decode('gbk').replace('\x00', ''), 
            'active': active, 
            'pre_close': pre_close, 
            'open': open, 
            'high': high, 
            'low': low, 
            'current': current, 
            'open_position': open_position, 
            'add_position': add_position, 
            'vol': vol, 
            'curr_vol': curr_vol, 
            'amount': amount, 
            'in_vol': in_vol, 
            'ex_vol': ex_vol, 
            'u14': u14, 
            'hold_position': hold_position,
            'pending': pending,
            'settlement_price': settlement_price,
            'average_price': average_price,
            'pre_settlement_price': pre_settlement_price,
            'pre_close_price': pre_close_price,
            'pre_vol': pre_vol,
            'day3_raise': day3_raise,
            'settlement_price2': settlement_price2,
            'date': date(date_raw // 10000, date_raw % 10000 // 100, date_raw % 100),
            'raise_speed': raise_speed,
            'u1': u1,
            'u2': u2,
            'u3': [u3, u4, u5, u6],
        }
    
@register_parser(0x23fa, 1)
class QuotesSingle(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B9s', category.value, code.encode('gbk'))
    
    @override
    def deserialize(self, data):
        return unpack_futures(data, 9)

@register_parser(0x23fb, 1)
class Quotes(BaseParser):
    def __init__(self, futures: list[EX_CATEGORY, str] = []):
        length = len(futures)
        if length <= 0:
            raise Exception('futures count must > 0')
        self.body = bytearray(struct.pack('<HHHHH', 2, 3148, 0, 600, length)) # TODO
        
        for category, code in futures:
            self.body.extend(struct.pack('<B23s', category.value, code.encode('gbk')))

    @override
    def deserialize(self, data):
        u, _, count = struct.unpack('<IIH', data[:10])
        results = []
        for i in range(count):
            results.append(unpack_futures(data[314 * i + 10: 314 * i + 324]))
        return results
    
@register_parser(0x23ff, 1)
class K_Line(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800):
        self.body = struct.pack('<B9sHHIH', category.value, code.encode('gbk'), period.value, times, start, count)
        
    @override
    def deserialize(self, data):
        category, name, period, times, _, count = struct.unpack('<B9sHHIH', data[:20])

        minute_category = period < 4 or period == 7 or period == 8

        bars = []
        for _ in range(count):
            date_num, open, high, low, close, amount, vol, _ = struct.unpack('<IfffffIf', data[20 + 32 * _ : 20 + 32 * _ + 32])
            
            bars.append({
                'time': to_datetime(date_num, minute_category),
                'open': open,
                'high': high,
                'low': low,
                'close': close,
                'amount': amount,
                'vol': vol,
            })
        return bars
    
# @register_parser(0x240b, 1)
# class Chart(BaseParser): # 疑似废弃旧接口
#     def __init__(self, category: EX_CATEGORY, code: str):
#         self.body = struct.pack('<B9s', category.value, code.encode('gbk'))

#     @override
#     def deserialize(self, data):
#         category, code, count = struct.unpack('<B9sH', data[:12])

#         result = []
#         for i in range(count):
#             minutes, price, avg, vol, _ = struct.unpack('<HffII', data[i * 18 + 12: i * 18 + 30])
#             result.append({
#                 'time': time(minutes // 60, minutes % 60),
#                 'price': price,
#                 'avg': avg,
#                 'vol': vol
#             })
#         return result
    
# >1224 e8013501 2a 543030390000000000000000000000000000000000000000000000000000000000000000000000 000000007800
# >1224 90013501 4a 4141504c0000000000000000000000000000000000000000000000000000000000000000000000 000000007800
# >1224 57023501 4a 41414d490000000000000000000000000000000000000000000000000000000000000000000000 000000007800
# >1224 a5d93401 4a 414143495500000000000000000000000000000000000000000000000000000000000000000000 000000007800
# >1224 e9013501 1b 4345534d0000000000000000000000000000000000000000000000000000000000000000000000 780000008403
# >1224 e9013501 1b 4345534d0000000000000000000000000000000000000000000000000000000000000000000000 fc0300008403
# >1224 ee013501 1f 303030323500000000000000000000000000000000000000000000000000000000000000000000 000000007800
@register_parser(0x2412, 1)
class HistoryTransaction(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str, date: date):
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack('<IB43sH', date, category.value, code.encode('gbk'), 0x78)
        
    @override
    def deserialize(self, data):
        category, name, date, start_price, _, _, count = struct.unpack('<B39sIfIIH', data[:58])

        results = []
        for _ in range(count):
            minutes, price, vol, u, buy_sell = struct.unpack('<HIIIH', data[58 + 16 * _ : 58 + 16 * _ + 16])
            results.append({
                'time': time(minutes // 60 % 24, minutes % 60),
                'price': price,
                'vol': vol,
                'action': ['BUY', 'SELL', 'NEUTRAL'][buy_sell]
            })

        return results
     
@register_parser(0x2422, 1)
class Table(BaseParser):
    def __init__(self, start: int = 0, mode: int = 1):
        self.body = bytearray(struct.pack('<II16s85xB16x', start, 0, bytes.fromhex('00781f0e6a37447b502b7c0d01404c0a'), mode))

    @override
    def deserialize(self, data):
        start, = struct.unpack('<I', data[35:39])
        count, ctx_len = struct.unpack('<II', data[161:169])
        ctx = data[169:].decode('gbk',errors='ignore').replace('\x00', '')
        return start, count, ctx
     
@register_parser(0x2423, 1)
class TableDetail(Table):
    def __init__(self, start: int = 0, mode: int = 0):
        super().__init__(start, mode)

# > 5424e5bb1c2fafe525941f32c6e5d53dfb415b734cc9cdbf0ac91f3b71a6861a5dce67c7dd2b6f5552dfef9257c6ad5547831f32c6e5d53dfb411f32c6e5d53dfb41a9325ac935dc0837335a16e4ce17c1bb
# TODO

@register_parser(0x2458, 1)
class Meta(file.Meta):
    pass
    
@register_parser(0x2459, 1)
class Download(file.Download):
    def __init__(self, file_name: str, start: int = 0, size: int = 0x7530):
        self.body = struct.pack('<II40s', start, size, file_name.encode('gbk'))

@register_parser(0x2484, 1)
class Futures_QuotesList(Quotes):
    def __init__(self, category: EX_CATEGORY, start: int = 0, count: int = 100):
        self.body = struct.pack('<BHHHH', category.value, 0, start, count, 1)   

@register_parser(0x2487, 1)
class f2487(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B23s', category.value, code.encode('gbk'))

    @override
    def deserialize(self, data):
        category, code = struct.unpack('<B23s', data[:24])
        
        active, pre_close, open, high, low, close, u1, price = struct.unpack('<I7f', data[24:56])
        vol, curr_vol, amount = struct.unpack('<IIf', data[56:68])
        
        a = struct.unpack('<4I', data[68:84])
        b = struct.unpack('<HII24fB10fHB', data[164:])
        print(a,b)
        print(data[84:164].hex())
        
        return {
            'category': EX_CATEGORY(category), 
            'code': code.decode('gbk').replace('\x00', ''), 
            'active': active, 
            'pre_close': pre_close, 
            'open': open, 
            'high': high, 
            'low': low, 
            
            'vol': vol, 
            'curr_vol': curr_vol, 
            'amount': amount, 
        }

# > 8824 22 3030303031300000000000000000000000000000000000 0000 0000 3700 0000000000000000
@register_parser(0x2488, 1) # TODO
class f2488(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B23sIHII', category.value, code.encode('gbk'), 0, 55, 0, 0)

    @override
    def deserialize(self, data):
        category, code, count = struct.unpack('<B35sH', data[:38])
        print(EX_CATEGORY(category), code.decode('gbk').replace('\x00', ''))

        for i in range(count):
            z = struct.unpack('<I6H', data[i * 16 + 38: i * 16 + 54])
            print(z)
        return None
    
@register_parser(0x2489, 1)
class K_Line_2(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800):
        self.body = struct.pack('<B23sHHII16x', category.value, code.encode('gbk'), period.value, times, start, count)

    @override
    def deserialize(self, data):
        category, name, period, times, start, _, _, count = struct.unpack('<B23sHHIIIH', data[:42])

        minute_category = period < 4 or period == 7 or period == 8

        results = []
        for i in range(count):
            date_num, open, high, low, close, amount, vol, _ = struct.unpack('<IfffffII', data[42 + 32 * i: 42 + 32 * i + 32])
            
            results.append({
                'date': to_datetime(date_num, minute_category),
                'open': open,
                'high': high,
                'low': low,
                'close': close,
                'amount': amount,
                'vol': vol,
            })
        return results

# > 8a24 00 00000030750000 
# > 8a24 00 00303032313132 
# > 8a24 01 00003030323131 
# > 8a24 01 00013939393939 
# > 8a24 04 00003339393030 
# > 8a24 05 00000000000000 
# > 8a24 06 002e0000000900 
# > 8a24 07 00013939393939 
# > 8a24 1b 4345534d000000 
# > 8a24 1c 0052534c390000 
# > 8a24 1f 30303030310000 
# > 8a24 1f 30333636380000 
# > 8a24 1f 30363631330000 
# > 8a24 21 00303030303134 
# > 8a24 21 00303030303230 
# > 8a24 21 00303030303432 
# > 8a24 2c 38373430393000 
# > 8a24 2c 38393930303100 
# > 8a24 46 00484b31303231 
# > 8a24 46 00484b31303333 
# > 8a24 46 00484b31303532 
# > 8a24 46 00484b31303831 
# > 8a24 46 484b3032313000 
# > 8a24 49 00000000280001 
# > 8a24 4a 0000a8002a0001 
# > 8a24 4a 42414241000000 
# > 8a24 4a 4a4e5547000000 
# > 8a24 4e 44303500000000 
# > 8a24 e9 0135011b434553 
@register_parser(0x248a, 1) # TODO 前8位不明所以
class Futures_Quotes(Quotes):
    def __init__(self, futures: list[int, str]):
        length = len(futures)
        if length <= 0:
            raise Exception('futures count must > 0')
        self.body = bytearray(struct.pack('<B7xH', 5, length))
        
        for category, code in futures:
            self.body.extend(struct.pack('<B23s', category.value, code.encode('gbk')))

# > 8b24 0a 555344434e480000000000000000000000000000000000 0400010000000000
# > 8b24 0c 415f485843000000000000000000000000000000000000 0400010000000000
# > 8b24 0c 434e593000000000000000000000000000000000000000 0000000000000000
# > 8b24 17 4853494c38000000000000000000000000000000000000 0400010000000000
# > 8b24 1b 4345534d00000000000000000000000000000000000000 0000000000000000
# > 8b24 1f 3036363133000000000000000000000000000000000000 0238393930353001
# > 8b24 1f 3036383231000000000000000000000000000000000000 0000000000000000
# > 8b24 2c 3837343039300000000000000000000000000000000000 0400010000000000
# > 8b24 2c 3839393030310000000000000000000000000000000000 0000000000000000
# > 8b24 2f 49464c3800000000000000000000000000000000000000 0138383037393701
# > 8b24 2f 544c320000000000000000000000000000000000000000 0000000000000000
# > 8b24 2f 544c323630360000000000000000000000000000000000 0000000000000000
# > 8b24 44 5458303030310000000000000000000000000000000000 0000000000000000
# > 8b24 46 484b303231300000000000000000000000000000000000 0000000000000000
# > 8b24 46 5553303430320000000000000000000000000000000000 0000000000000000
# > 8b24 46 5553303435330000000000000000000000000000000000 0000000000000000
# > 8b24 4a 4352434c00000000000000000000000000000000000000 0000000000000000
# > 8b24 4a 59414e4700000000000000000000000000000000000000 0400010000000000
# > 8b24 4a 59494e4e00000000000000000000000000000000000000 0400010000000000
# > 8b24 4a 5a53455000000000000000000000000000000000000000 0000000000000000
# > 8b24 4e 4430350000000000000000000000000000000000000000 0000000000000000
@register_parser(0x248b, 1) # TODO 后8位不明所以
class TickChart(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B23s8x', category.value, code.encode('gbk'))
    
    @override
    def deserialize(self, data):
        category, code, count = struct.unpack('<B31sH', data[:34])
        # print(EX_CATEGORY(category), code.decode('gbk').replace('\x00', ''))

        charts = []
        for i in range(count):
            minutes, price, avg, vol, _ = struct.unpack('<HffII', data[i * 18 + 34: i * 18 + 52])
            charts.append({
                'time': time(minutes // 60 % 24, minutes % 60),
                'price': price,
                'avg': avg,
                'vol': vol
            })
        return charts

# > 8c24 e0013501 1c 434a4c3800000000000000000000000000000000000000 000000000000 2f49
# > 8c24 31013501 1c 434a4c3800000000000000000000000000000000000000 393938f94902 0001
# > 8c24 73253501 1c 434a4c3800000000000000000000000000000000000000 000000000000 2f49
# > 8c24 f8013501 1c 434a4c3800000000000000000000000000000000000000 303530aa5502 0000
# > 8c24 94013501 4a 46484e2d43000000000000000000000000000000000000 000000000000 0001
#        94013501 4a 46484e2d43000000000000000000000000000000000000 000000000000 0001
@register_parser(0x248c, 1) # TODO 后8位不明所以
class HistoryTickChart(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str, date: date):
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack('<IB23s6sH', date, category.value, code.encode('gbk'), b'', 0)

    @override
    def deserialize(self, data):
        category, name, date, avg_price, _, _, count = struct.unpack('<B23sIfIIH', data[:42])
        charts = []
        for i in range(count):
            minutes, price, avg ,vol, u = struct.unpack('<HffII', data[42 + 18 * i : 42 + 18 * i + 18])
            charts.append({
                'time': time(minutes // 60 % 24, minutes % 60),
                'price': price,
                'avg': avg,
                'vol': vol
            })
        return charts
    
# > 4d25 4a00 4352434c000000000000000000000000000000000000 0100 1400 000000000000000000
# > 4d25 2f00 54534c39000000000000000000000000000000000000 0100 1400 000000000000000000
# > 4d25 4600 484b3130313100000000000000000000000000000000 0100 1400 000000000000000000
# > 4d25 2f00 49484c39000000000000000000000000000000000000 0100 1400 000000000000000000 01b62d880000340234028a242f0049484c39000017002a54303336000000000000000000000000000000000000002f49434c39000000000000000000000000000000000000002f49464c39000000000000000000000000000000000000002f49484c39000000000000000000000000000000000000002f494d4c39000000000000000000000000000000000000002f54464c39000000000000000000000000000000000000002f544c3900000000000000000000000000000000000000002f544c4c39000000000000000000000000000000000000002f54534c39000000000000000000000000000000000000001c41504c39000000000000000000000000000000000000001c43464c39000000000000000000000000000000000000001c434a4c39000000000000000000000000000000000000001c43594c39000000000000000000000000000000000000001c46474c39000000000000000000000000000000000000001c4d414c39000000000000000000000000000000000000001c4f494c39000000000000000000000000000000000000001c50464c39000000000000000000000000000000000000001c504b4c39000000000000000000000000000000000000001c504c4c39000000000000000000000000000000000000001c50524c39000000000000000000000000000000000000001c50584c39000000000000000000000000000000000000001c524d4c39000000000000000000000000000000000000001c52534c3900000000000000000000000000000000000000
# > 4d25 1b00 43455347313000000000000000000000000000000000 0100 1400 000000000000000000 01a42d880000340234028a241b0043455347313017001b43455331303000000000000000000000000000000000001b43455331323000000000000000000000000000000000001b43455332383000000000000000000000000000000000001b43455333303000000000000000000000000000000000001b43455341383000000000000000000000000000000000001b43455347313000000000000000000000000000000000001b434553484b4200000000000000000000000000000000001b4345534d000000000000000000000000000000000000001b43455350353000000000000000000000000000000000001b47454d00000000000000000000000000000000000000001b484b4c00000000000000000000000000000000000000001b48534900000000000000000000000000000000000000001b485a3530313400000000000000000000000000000000001b485a3530313500000000000000000000000000000000001b485a3530313600000000000000000000000000000000001b485a3530313700000000000000000000000000000000001b485a3530313800000000000000000000000000000000001b485a3530323000000000000000000000000000000000001b485a3530323100000000000000000000000000000000001b485a3530323200000000000000000000000000000000001b485a3530323300000000000000000000000000000000001b485a3530323400000000000000000000000000000000001b485a353032350000000000000000000000000000000000
@register_parser(0x254d, 1) # TODO 有时会跟一段莫名hex
class ChartSampling(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<H22sHH9x', category.value, code.encode('gbk'), 1, 20)

    @override
    def deserialize(self, data):
        category, code, a,b,c,d,e,f,g,h, count = struct.unpack('<H22s9H', data[:42])
        print(a,b,c,d,e,f,g,h, count)
        
        prices = []
        for i in range(count):
            p, = struct.unpack('<f', data[i * 4 + 42: i * 4 + 46])
            prices.append(p)
            
        return prices


@register_parser(0x2562, 1)
class f2562(BaseParser):
    def __init__(self, market: int, start: int = 0, count: int = 600):
        self.body = struct.pack(u'<HII', market, start, count)

    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])
        result = []
        
        for i in range(count):
            category, name, u, index, switch, u2, u3, u4, u5, u6 = struct.unpack('<H23sHIBfffHH', data[48 * i + 2: 48 * i + 50])
            result.append({
                'name': name.decode('gbk').replace('\x00', ''),
                'category': category,
                'u': u,
                'index': index,
                'switch': switch,
                'code': [u2, u3, u4, u5, u6]
            })
        return result