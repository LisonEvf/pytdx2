import struct

from parser.baseParser import BaseParser, register_parser


@register_parser(0x23f0, 1)
class Count(BaseParser): # ?
    def deserialize(self, data):
        id, _, _, count, _, _ = struct.unpack('<11s5I', data[:31])
        return count