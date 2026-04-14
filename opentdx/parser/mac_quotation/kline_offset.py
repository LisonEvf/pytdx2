import struct
from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x124A, 1)
class KlineOffset(BaseParser):
    def __init__(self, offset: int = 0, count: int = 128000):
        self.body = struct.pack('<II5x', offset, count)

    def deserialize(self, data):
        if len(data) < 8:
            return []
        offset, total = struct.unpack_from('<II', data, 0)
        results = []
        pos = 8
        row_length = 34
        while pos + row_length <= len(data):
            row = data[pos:pos + row_length]
            # check if this is a valid entry (code should be ASCII digits)
            code_byte = row[0]
            code_ascii = row[1:7]
            if not all(0x30 <= b <= 0x39 for b in code_ascii):
                pos += 1
                continue
            code = (chr(code_byte + 0x30) if code_byte == 0 else code_ascii.decode('ascii', errors='replace'))
            if code_byte == 0:
                code = '0' + code_ascii.decode('ascii')
            else:
                code = code_ascii.decode('ascii')
            name = row[7:15].decode('gbk', errors='replace').rstrip('\x00')
            short_name = row[23:27].decode('ascii', errors='replace').rstrip('\x00')
            market = row[33]
            results.append({
                'market': market,
                'code': code,
                'name': name,
                'short_name': short_name,
            })
            pos += row_length
        return results
