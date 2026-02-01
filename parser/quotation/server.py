from datetime import date, datetime
import struct
from typing import override

from utils.log import log
from parser.baseparser import BaseParser, register_parser


# >0c 07189500 01 0200 0200 |0200
# <b1cb7400 0c 07189500 00 0200 0200 0200 |0000
@register_parser(0x2) # Login后
class ExchangeAnnouncement(BaseParser):   
    @override
    def deserialize(self, data):
        v, = struct.unpack('<B', data[:1])
        return {
            'v': v,
            'content': data[1:].decode('gbk')
        }

# >0c 07189500 01 0200 0200 |0400
# <b1cb7400 0c 07189500 00 0400 0a00 0a00 |000000000000 a2ff3401
@register_parser(0x4) # 心跳包15秒
class HeartBeat(BaseParser):
    @override
    def deserialize(self, data):
        (_, date) = struct.unpack('<6sI', data[:10])
        return date

@register_parser(0xa) # 服务商公告
class Announcement(BaseParser):
    def __init__(self):
        self.body = struct.pack('<54s', b'')
    @override
    def deserialize(self, data):
        had, = struct.unpack('<B', data[:1])
        if had == 0x01:
            (expire_date, title_len, author_len, conntent_len) = struct.unpack('<IHHH', data[1:11])
            (title, author, content) = struct.unpack(f'<{title_len}s{author_len}s{conntent_len}s', data[11:11+title_len+author_len+conntent_len])
            expire_date = date(expire_date // 10000, expire_date % 10000 // 100, expire_date % 100)
            return {
                'expire_date': expire_date,
                'title': title.decode('gbk'),
                'author': author.decode('gbk'),
                'content': content.decode('gbk')
            }
        else:
            return None


# <b1cb7400 0c 01187b00 00 0b00 5000 5000 |01000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#                                          6d4a 391e 0200
#                                          a2ff3401 0001 00000000000000000000000000000000
@register_parser(0xb)#TODO: 未完成
class TodoB(BaseParser):
    def __init__(self):
        self.body = bytearray()
    @override
    def deserialize(self, data):
        return data

# >0c 02189400 01 0300 0300 |0d00 01
# <b1cb7400 1c 02189400 00 0d00 5000 bd00 |789c6378c9cec826c9c72069c5b4898987b9050ed1f90c8bfe9b304a7a3182692920fd9fe13903032323e37f8693e7772d3ebdfafcfd6bdfafee3364a016600421e5b32bb6bcbf701487120051371e55
#                                          00 e907 01 06 10 17 00 2b 
#                                      ?   3a02b2020c0384038403840384038403 3a02b2020c0384038403840384038403 00
#                                      ?   a2ff3401 1a4a 0100 a2ff3401 1b4a 0100
#                                      ?   ff00 e700 00010101ff
#                                          00c9cfbaa3cbabcfdfd6f7d5be330000000000000000
#                                          00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
#                                      ?   000100000100
#                                          23cda8b4efd0c50000000000000000000000000000000000000000000000
@register_parser(0xd)
class Login(BaseParser):
    def __init__(self):
        self.body = struct.pack('<B', 1)

    @override
    def deserialize(self, data):
        (_, year, day, month, minute, hour, _, second, \
        unknown1, unknown2, unknown3, \
        date, a1, b1, date2, a2, b2, \
        unknown4, unknown5, unknown6, \
        server_name, web_site, unknown7, category) = struct.unpack('<BHBBBBBB16s16sBIHHIHHHH5s22s64s6s30s', data)

        # print(f'a1: {a1} b1: {b1} a2: {a2} b2: {b2}')
        # print(f"unknown1: {unknown1.hex()} unknown2: {unknown2.hex()} unknown3: {unknown3} unknown4: {unknown4} unknown5: {unknown5} unknown6: {unknown6.hex()}")

        info = {
            "date_time": datetime(year, month, day, hour, minute, second).strftime('%Y-%m-%d %H:%M:%S'),
            "server_name": server_name.decode('gbk').replace('\x00', ''),
            "web_site": web_site.decode('gbk').replace('\x00', ''),
            "category": category.decode('gbk').replace('\x00', ''),
        }
        return info

# >0c 00000000 00 0200 0200 |1500 
# <b1cb7400 1c 00000000 00 1500 7f00 ab01 |789c6b67636050f06380024606230323530353638378030b137303730638f0c9cc2bad303351500833d33337306440053c5fb41918fe678a3230ea97a454e867e41797e4e8338c40606a646a6260606964626c6602135bf4df8451dc8b91818189899191118ba61486130ca0c07f0954b84f8709ac011d3330000011c120f2
# 05070000 204e0000 00000000 0000 0100
# 32303235303533305f303834373038000000000000000000004c696e75783634202056362e373031
# 0000000000000000000000000000000cd02b00006149190001
# 2f7464782f686f73746c2f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003532353430303236343831380000000000000000
# a2ff3401 184a 0100 000202010101 00000000000000000000000000000000000000
# 6400 c800 0000 0100
# e9ff3401 693b0300 a2ff3401 a2ff3401 a2ff3401 a2ff3401 a2ff3401
# 0000
@register_parser(0x15)
class Info(BaseParser):
    def __init__(self):
        self.body = bytearray()
                                      
    @override
    def deserialize(self, data):
        # Region: 可能是大区？， 东区100：上海、深圳  北区90：北京  南区80：上海、广州 中区25：武汉  西区56：成都
        maybe_delay, unknown_aH, _, unknown_bH, info, unknown10s, content, server_sign, date1, unknown_cH, unknown_dH, unknown6s, \
            _, Region, unknown_fH, _, maybe_switch, \
                date_now, time_now, date3, date4, date5, date6, date7, z  = struct.unpack('<IH8sH55s10s255s20sIHH6s19sHHHHIIIIIIIH', data[:427])
        
        print(maybe_delay, unknown_aH, _, unknown_bH, unknown10s, date1, unknown_cH, unknown_dH, unknown6s, Region, unknown_fH, maybe_switch, date_now, time_now, date3, date4, date5, date6, date7, z)
        time_now = datetime(date_now // 10000, date_now % 10000 // 100, date_now % 100, time_now // 10000, time_now % 10000 // 100, time_now % 100)
        return {
            "delay": maybe_delay,
            "info": info.decode('gbk').replace('\x00', ''),
            "content": content.decode('gbk').replace('\x00', ''),
            "server_sign": server_sign.decode('gbk').replace('\x00', ''),
            "time_now": time_now.strftime('%Y-%m-%d %H:%M:%S'),
            "unknown1": [unknown_aH, unknown_bH, unknown10s.hex()],
            "unknown2": [unknown_cH, unknown_dH, unknown6s.hex()],
            "unknown3": [Region, unknown_fH, maybe_switch],
        }
#

# >0c 09187100 01 0200 0200 |de0f
# <b1cb740 01 c09187100 00 de0f 1d00 bb00 |789c63606060606418122093a1298081614312038330d8c5001df70263
# 00000000 0100
# 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# 690082500000b0620000130100000000
@register_parser(0xfde)
class TodoFDE(BaseParser):
    @override
    def deserialize(self, data):
        (u1, u2, u3, u4) = struct.unpack('<IH165s16s', data[:187])
        return {
            "unknown": [u1, u2, u4.hex()]
        }

# >0c 03189900 01 2000 2000 db0f |7464786c6576656c 000000a4 70 f5 40 07 0000000000000000000000000005
#                                                           -- -- -- --
# 这里 70f5和4007应该是两个版本号，4007对应的是像是V9.7,可是为什么呢？ 因为用400a时，V9.10的升级提示就没了
@register_parser(0xfdb)
class UpgradeTip(BaseParser):
    def __init__(self):
        self.body = bytearray(struct.pack('<8s', 'tdxlevel'.encode('gbk')))
        self.body.extend(bytearray().fromhex(u'00 00 00 a4 70 f5 40 07 00 00 00 00 00 00 00 00 00 00 00 00 00 05'))
        # self.body = bytearray(struct.pack('<8s', '招商证券'.encode('gbk')))
        # self.body.extend(bytearray().fromhex(u'00 00 00 8f c2 25 40 13 00 00 d5 00 c9 cc bd f0 d7 ea 00 00 00 02'))
                                      
    @override
    def deserialize(self, data):
        (had, unknow2, tips, unknow5, link) = struct.unpack('<BH50s5s120s', data[:178])
        tips = tips.decode('gbk').replace('\x00', '')
        link = link.decode('gbk').replace('\x00', '')
        msg = data[178:].decode('gbk', 'ignore').replace('\x00', '') if had == 0x01 else None
        return {
            "had": had,
            "unknown": [unknow2, unknow5.hex()],
            "tips": tips,
            "link": link,
            "msg": msg
        }