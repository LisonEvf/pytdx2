from datetime import datetime
from const import MARKET
from parser.baseparser import BaseParser, register_parser
import struct
from typing import override

@register_parser(0x2562, 1)
class f2562(BaseParser):
    def __init__(self, market: MARKET, start: int = 0, count: int = 600):
        self.body = struct.pack(u'<HII', market.value, start, count)
    @override
    def deserialize(self, data):
        print(data.hex())
        return data
    
@register_parser(0x2454, 1)
class Login(BaseParser):
    def __init__(self):
        self.body = bytearray.fromhex('' \
        'e5bb1c2fafe52594' \
        '1f32c6e5d53dfb41' \
        '5b734cc9cdbf0ac9' \
        '2021bfdd1eb06d22' \
        'd008884c1611cb13' \
        '78f6abd824d899d2' \
        '1f32c6e5d53dfb41' \
        '1f32c6e5d53dfb41' \
        'a9325ac935dc0837' \
        '335a16e4ce17c1bb')
    @override
    def deserialize(self, data):
        _, _, year, month, day, minute, hour, ms, second, server_name, u1, u2, u3, u4, u5, desc, u6, u7, u8, ip = struct.unpack('<B52sHBBBBBB21sfBHHH151sBBB52s', data)
        print({
            "date_time": datetime(year, month, day, hour, minute, second).strftime('%Y-%m-%d %H:%M:%S'),
            "server_name": server_name.decode('gbk').replace('\x00', ''),
            "desc": desc.decode('gbk').replace('\x00', ''),
            "ip": ip.decode('gbk').replace('\x00', ''),
            "unknown": [u1, u2, u3, u4, u5, u6, u7, u8]
        })
        return {
            "date_time": datetime(year, month, day, hour, minute, second).strftime('%Y-%m-%d %H:%M:%S'),
            "server_name": server_name.decode('gbk').replace('\x00', ''),
            "desc": desc.decode('gbk').replace('\x00', ''),
            "ip": ip.decode('gbk').replace('\x00', ''),
            "unknown": [u1, u2, u3, u4, u5, u6, u7, u8]
        }

@register_parser(0x2455, 1)
class Info(BaseParser):
    @override
    def deserialize(self, data):
        maybe_delay, u2, u3, u4, info, version = struct.unpack('<4I25s29s', data[:70])
        u5, u6, u7, u8, u9, date_now, time_now, f1, f2, u15, u16, u17, u18, date2, date3, date4, u22 = struct.unpack('<HHHHHIIffHHHBIIIH', data[70:117])
        server_sign, maybe_switch = struct.unpack('<13sB', data[117:131])
        
        name, = struct.unpack('<30s', data[159:189])
        a, u23, date5, s0, u24, date6, s1, u25, date7, date8 = struct.unpack('<18s5IB3I', data[189:240])
        server_sign2, = struct.unpack('<13s', data[240:253])
        u26, date9, date10, s2, date11, date12, date13, s3, u28, s4, u29 = struct.unpack('<IIIBIIIBfBH', data[253:286])
        date14, u30, date15, u31 = struct.unpack('<IfIf', data[311:327])
        
        # print(maybe_delay, u2, u3, u4)
        # print(u5, u6, u7, u8, u9, date_now, time_now, f1, f2, u15, u16, u17, u18, date2, date3, date4, u22)
        # print(data[131:159].hex(), a.hex())
        # print(u23, date5, f'|{s0}|', u24, date6, f'|{s1}|', u25, date7, date8)
        # print(u26, date9, date10, f'|{s2}|', date11, date12, date13, f'|{s3}|', u28, f'|{s4}|', u29)
        # print(date14, u30, date15, u31)
        # print(data[327:].hex())
        
        time_now = datetime(date_now // 10000, date_now % 10000 // 100, date_now % 100, time_now // 10000, time_now % 10000 // 100, time_now % 100)
        return {
            "delay": maybe_delay,
            "info": info.decode('gbk').replace('\x00', ''),
            "version": version.decode('gbk').replace('\x00', ''),
            "server_sign": server_sign.decode('gbk').replace('\x00', ''),
            "time_now": time_now.strftime('%Y-%m-%d %H:%M:%S'),
            "server_sign2": server_sign2.decode('gbk').replace('\x00', ''),
            "name": name.decode('gbk').replace('\x00', '')
        }