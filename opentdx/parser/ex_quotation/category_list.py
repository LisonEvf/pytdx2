
import struct
from typing import override

from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x23f4, 1)
class CategoryList(BaseParser):
    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])

        result = []
        for i in range(count):
            goods_type, name, code, abbr = struct.unpack('<B32sB30s', data[64 * i + 2: 64 * i + 66])
            goods_type = ['STOCK', 'HK', 'FUTURES', 'FX', 'INDEX', 'VALUATION', 'MONEY', 'FUND', 'MONETARY_FUND', 'INDICATOR', 'MIRROR', 'OPTION', 'US', 'DE', 'SG'][goods_type - 1]
            result.append({
                'goods_type': goods_type,
                'name': name.decode('gbk').replace('\x00', ''),
                'code': code,
                'abbr': abbr.decode('gbk').replace('\x00', '')
            })
        return result
    

# STOCK = 1               # 股票
# HK = 2                  # 香港
# FUTURES = 3             # 期货
# FX = 4                  # 汇率
# INDEX = 5               # 指数
# VALUATION = 6           # 估值
# MONEY = 7               # 资金
# FUND = 8                # 基金
# MONETARY_FUND = 9       # 货币基金
# INDICATOR = 10          # 指标
# MIRROR = 11             # 镜像
# OPTION = 12             # 期权
# US = 13                 # 美国
# DE = 14                 # 德国
# SG = 15                 # 新加坡