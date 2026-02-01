from const import EX_CATEGORY, EX_MARKET, PERIOD, MARKET
from parser.baseparser import BaseParser, register_parser
import struct
from typing import override
import six


@register_parser(0x23f0, 1)
class Count(BaseParser): # ?
    @override
    def deserialize(self, data):
        name, _, _, count, _, _ = struct.unpack('<11s5I', data[:31])
        
        return {
            'name': name.decode('gbk').replace('\x00', ''),
            'count': count
        }

@register_parser(0x23f4, 1)
class Category_List(BaseParser):
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
                'abbr': abbr.decode('gbk')
            })
        return result
    
@register_parser(0x23f5, 1)
class Info(BaseParser):
    def __init__(self, start, count):
        self.body = struct.pack('<IH', start, count)

    @override
    def deserialize(self, data):
        start, count = struct.unpack("<IH", data[:6])
        
        instruments = []
        for i in range(count):
            market, category, u3, u4, code, name, u5, u6, u7, u8, u9, u10, u11, u12, u13, u14 = struct.unpack("<BBBH9s26sffHHHHHHHH", data[i * 64 + 6: i * 64 + 70])

            instruments.append({
                "market": EX_MARKET(market),
                "category": EX_CATEGORY(category),
                "code": code.decode('gbk').replace('\x00', ''),
                "desc": [u3, u4, u5, u6, u7, u8, u9, u10, u11, u12, u13],
                "name": name.decode('gbk').replace('\x00', ''),
            })
        
        return instruments


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
    s1, pre_vol, u7, s2, u8, day3_raise, s3, settlement_price2, date, u9, raise_speed, u10, s4, u11, u12 = struct.unpack('<12sff12sff25sfIIff24sHB', data[179 + code_len: 291 + code_len])

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
            'date': date,
            'raise_speed': raise_speed,
            'u1': u1,
            'u2': u2,
            'u3': [u3, u4, u5, u6],
        }
    
@register_parser(0x23fa, 1)
class Quotes(BaseParser):
    def __init__(self, category: EX_CATEGORY, code: str):
        self.body = struct.pack('<B9s', category.value, code.encode('gbk'))
    
    @override
    def deserialize(self, data):
        return unpack_futures(data, 9)

@register_parser(0x23fb, 1)
class QuotesList(BaseParser):
    def __init__(self, futures: list[EX_CATEGORY, str] = []):
        length = len(futures)
        if length <= 0:
            raise Exception("futures count must > 0")
        self.body = bytearray(struct.pack('<HHHHH', 2, 3148, 0, 600, length))
        
        for future in futures:
            category, code = future

            if type(code) is six.text_type:
                code = code.encode("gbk")
            self.body.extend(struct.pack('<B23s', category.value, code))

    @override
    def deserialize(self, data):
        u, _, count = struct.unpack('<IIH', data[:10])
        results = []
        for i in range(count):
            results.append(unpack_futures(data[314 * i + 10: 314 * i + 324]))
        return results
    
@register_parser(0x23ff, 1)
class Bars(BaseParser):
    def __init__(self, market: MARKET, code: str, period: PERIOD, start: int = 0, count: int = 800):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack('<B9sHHIH', market, code, period, 1, start, count)
        
        self.period = period
        
    @override
    def deserialize(self, data):
        return data
     
@register_parser(0x2422, 1)
class Futures_List(BaseParser):
    def __init__(self, start: int = 0, mode: int = 1):
        self.body = bytearray(struct.pack('<II16s85xB16x', start, 0, bytes.fromhex('00781f0e6a37447b502b7c0d01404c0a'), mode))

    @override
    def deserialize(self, data):
        start, = struct.unpack('<I', data[35:39])
        count, ctx_len = struct.unpack('<II', data[161:169])
        ctx = data[169:].decode('gbk',errors='ignore').replace('\x00', '')
        return start, count, ctx
     
@register_parser(0x2423, 1)
class Futures_List2(Futures_List):
    def __init__(self, start: int = 0, mode: int = 0):
        super().__init__(start, mode)
    

@register_parser(0x2484, 1)
class Futures_QuotesList(QuotesList):
    def __init__(self, category: EX_CATEGORY, start: int = 0, count: int = 100):
        self.body = struct.pack('<BHHHH', category.value, 0, start, count, 1)   
    
@register_parser(0x248a, 1)
class Futures_Quotes(QuotesList):
    def __init__(self, futures: list[int, str]):
        length = len(futures)
        if length <= 0:
            raise Exception("futures count must > 0")
        self.body = bytearray(struct.pack('<HHHHH', 2, 0, 0, 600, length))
        
        for future in futures:
            category, code = future

            if type(code) is six.text_type:
                code = code.encode("gbk")
            self.body.extend(struct.pack('<B23s', category.value, code))
    