import struct
from typing import override
from const import MARKET
from parser.baseparser import BaseParser, register_parser
import six
from utils.help import to_datetime

@register_parser(0x2cf)
class Category(BaseParser):
    def __init__(self, market: MARKET, code: str):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack("<H6sI", market.value, code, 0)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])

        def get_str(str):
            pos = str.find(b'\x00')
            if pos != -1:
                str = str[:pos]
            try:
                return str.decode('gbk')
            except:
                return 'unknown str'


        categories = []
        for i in range(count):
            category_buf = data[2 + i * 152:2 + (i + 1) * 152]

            (name, filename, start, length) = struct.unpack("<64s80sII", category_buf)
            categories.append({
                'name': get_str(name),
                'filename': get_str(filename),
                'start': start,
                'length': length,
            })

        return categories

@register_parser(0x2d0)
class Content(BaseParser):
    def __init__(self, market: MARKET, code: str, filename: str, start: int, length: int):
        if type(code) is six.text_type:
            code = code.encode("utf-8")

        if type(filename) is six.text_type:
            filename = filename.encode("utf-8")

        if len(filename) != 80:
            filename = filename.ljust(80, b'\x00')

        self.body = struct.pack(u"<H6sH80sIII", market.value, code, 0, filename, start, length, 0)

    @override
    def deserialize(self, data):
        (market, code, marketOR, length) = struct.unpack(u"<H6sHH", data[:12])

        return {
            'market': market,
            'code': code,
            'marketOR': marketOR,
            'length': length,
            'content': data[12:12+length].decode('gbk', 'ignore').rstrip("\x00"),
        }


@register_parser(0x10)
class Finance(BaseParser):
    def __init__(self, market: MARKET, code: str):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u"<HB6s", 1, market.value, code)

    @override
    def deserialize(self, data):
        (
            num,
            market,
            code,
            liutongguben,
            province,
            industry,
            updated_date,
            ipo_date,
            zongguben,
            guojiagu,
            FaQiRenFaRenGu,
            FaRenGu,
            BGu,
            HGu,
            MeiGuShouYi,
            ZiChanZongJi,
            LiuDongZiChanZongJi,
            GuDingZiChanJinE,
            WuXingZiChan,
            GuDongRenShu,
            LiuDongFuZhaiHeJi,
            changqifuzhai,
            ZiBenGongJiJin,
            GuiMuQuanYiHeJi,
            YinYeZongShouRu,
            YinYeChengBen,
            YingShouZhangKuan,
            YinYeLiRun,
            TouZiShouYi,
            JingYinXianJinLiuJinE,
            zongxianjinliu,
            CunHuo,
            LiRunZongE,
            ShuiHouLiRun,
            GuiMuJinLiRun,
            WeiFenLiRun,
            MeiGuJinZiChan,
            baoliu2
        ) = struct.unpack("<HB6sfHHIIffffffffffffffffffffffffffffff", data)

        return {
            'market': MARKET(market),
            'code': code.decode('utf-8'),
            'liutongguben': liutongguben,
            'province': province,
            'industry': industry,
            'updated_date': updated_date,
            'ipo_date': ipo_date,
            'zongguben': zongguben,
            'guojiagu': guojiagu,
            'FaQiRenFaRenGu': FaQiRenFaRenGu,
            'FaRenGu': FaRenGu,
            'BGu': BGu,
            'HGu': HGu,
            'MeiGuShouYi': MeiGuShouYi,
            'ZiChanZongJi': ZiChanZongJi,
            'LiuDongZiChanZongJi': LiuDongZiChanZongJi,
            'GuDingZiChanJinE': GuDingZiChanJinE,
            'WuXingZiChan': WuXingZiChan,
            'GuDongRenShu': GuDongRenShu,
            'LiuDongFuZhaiHeJi': LiuDongFuZhaiHeJi,
            'changqifuzhai': changqifuzhai,
            'ZiBenGongJiJin': ZiBenGongJiJin,
            'GuiMuQuanYiHeJi': GuiMuQuanYiHeJi,
            'YinYeZongShouRu': YinYeZongShouRu,
            'YinYeChengBen': YinYeChengBen,
            'YingShouZhangKuan': YingShouZhangKuan,
            'YinYeLiRun': YinYeLiRun,
            'TouZiShouYi': TouZiShouYi,
            'JingYinXianJinLiuJinE': JingYinXianJinLiuJinE,
            'zongxianjinliu': zongxianjinliu,
            'CunHuo': CunHuo,
            'LiRunZongE': LiRunZongE,
            'ShuiHouLiRun': ShuiHouLiRun,
            'GuiMuJinLiRun': GuiMuJinLiRun,
            'WeiFenLiRun': WeiFenLiRun,
            'MeiGuJinZiChan': MeiGuJinZiChan,
            'baoliu2': baoliu2
        }


@register_parser(0xf)
class XDXR(BaseParser):
    def __init__(self, market: MARKET, code: str):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<HB6s', 1, market.value, code)

    @override
    def deserialize(self, data):
        (market, marketOR, code, count) = struct.unpack('<HB6sH', data[:11])

        xdxrs = []
        for i in range(count):
            pos = 11 + i * 29
            (market, code, unknown, date, category) = struct.unpack('<B6sBIB', data[pos: pos + 13])
            date = to_datetime(date)

            name = XDXR_CATEGORY_MAPPING.get(category, category)

            left_data = data[pos + 13: pos + 29]
            fenhong, peigujia, songzhuangu, peigu = None, None, None, None
            suogu = None
            xingquanjia, fenshu = None, None
            panqianliutong, qianzongguben, panhouliutong, houzongguben = None, None, None, None
            if category == 1:
                fenhong, peigujia, songzhuangu, peigu  = struct.unpack("<ffff", left_data)
            elif category in [11, 12]:
                _, _, suogu, _ = struct.unpack("<ffff", left_data)
            elif category in [13, 14]:
                xingquanjia, _, fenshu, _ = struct.unpack("<ffff", left_data)
            else:
                panqianliutong, qianzongguben, panhouliutong, houzongguben = struct.unpack("<ffff", left_data)

            xdxrs.append({
                'market': MARKET(market),
                'code': code,
                'date': date,
                'name': name,
                'fenhong': fenhong,
                'peigujia': peigujia,
                'songzhuangu': songzhuangu,
                'peigu': peigu,
                'suogu': suogu,
                'xingquanjia': xingquanjia,
                'fenshu': fenshu,
                'panqianliutong': panqianliutong,
                'qianzongguben': qianzongguben,
                'panhouliutong': panhouliutong,
                'houzongguben': houzongguben,
            })
        return xdxrs

XDXR_CATEGORY_MAPPING = {
    1 : "除权除息",
    2 : "送配股上市",
    3 : "非流通股上市",
    4 : "未知股本变动",
    5 : "股本变化",
    6 : "增发新股",
    7 : "股份回购",
    8 : "增发新股上市",
    9 : "转配股上市",
    10 : "可转债上市",
    11 : "扩缩股",
    12 : "非流通股缩股",
    13 : "送认购权证",
    14 : "送认沽权证"
}