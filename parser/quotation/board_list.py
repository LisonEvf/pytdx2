# Contribute by @biner
import struct
from typing import override

from const import BOARD_TYPE, MARKET
from parser.baseParser import BaseParser, register_parser


@register_parser(0x1231, 1)
class BoardList(BaseParser):
    def __init__(self, board_type :BOARD_TYPE = BOARD_TYPE.ALL ,start: int = 0, page_size :int = 300):
        sort_type = 0 # 1:根据涨速排序  0:根据涨幅排序。2:未知。
        sort_order = 1 # 不确定 sort_type 和 sort_order 具体如何联动
        self.body = struct.pack('<HHBBHH8x', page_size, board_type.value, sort_type,  sort_order, start, 1 )

    @override
    def deserialize(self, data):
        _, count = struct.unpack('<HH', data[:4])

        result = []
        for i in range(count):
            market, code, name, price, rise_speed, pre_close = struct.unpack('<H22s44sfff', data[i * 160 + 4: i * 160 + 84])
            symbol_market, symbol_code, symbol_name, symbol_price, symbol_rise_speed, symbol_pre_close = struct.unpack('<H22s44sfff', data[i * 160 + 84: i * 160 + 164])
            result.append({
                'market': MARKET(market),
                'code': code.decode('gbk').replace('\x00', ''),
                'name': name.decode('gbk').replace('\x00', ''),
                'price': price,
                'rise_speed': rise_speed,
                'pre_close': pre_close,
                'symbol_market': MARKET(symbol_market),
                'symbol_code': symbol_code.decode('gbk').replace('\x00', ''),
                'symbol_name': symbol_name.decode('gbk').replace('\x00', ''),
                'symbol_price': symbol_price,
                'symbol_rise_speed': symbol_rise_speed,
                'symbol_pre_close': symbol_pre_close,
            })
        
        return result