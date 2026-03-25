
import struct
from typing import override

from tdx_mcp.const import EX_MARKET
from tdx_mcp.parser.baseParser import BaseParser, register_parser


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