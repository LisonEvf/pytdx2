from opentdx.parser.baseParser import BaseParser, register_parser


@register_parser(0x120F, 1)
class ServerInit(BaseParser):
    def __init__(self):
        # Fixed 68-byte init body from proto.txt
        header = bytes.fromhex('04002d31')
        self.body = header + b'\x00' * 8 + b'\x00\x27\x06\x0e' + b'\x00' * 52

    def deserialize(self, data):
        return len(data) > 0 and data[0] == 0
