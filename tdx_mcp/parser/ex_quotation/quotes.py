import struct
# from typing import override  # Python 3.12+ only

from tdx_mcp.const import EX_CATEGORY
from tdx_mcp.parser.baseParser import BaseParser, register_parser
from tdx_mcp.utils.help import unpack_futures

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
class Quotes(BaseParser):
    def __init__(self, code_list: list[tuple[EX_CATEGORY, str]]):
        length = len(code_list)
        if length <= 0:
            raise Exception('futures count must > 0')
        self.body = bytearray(struct.pack('<B7xH', 5, length))
        
        for category, code in code_list:
            self.body.extend(struct.pack('<B23s', category.value, code.encode('gbk')))

    # @override  # Python 3.12+ only
    def deserialize(self, data):
        u, _, count = struct.unpack('<IIH', data[:10])
        results = []
        for i in range(count):
            results.append(unpack_futures(data[314 * i + 10: 314 * i + 324]))
        return results