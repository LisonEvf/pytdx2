import struct

class BaseParser:
    
    msg_id = 0
    body = bytearray()
    customize = 0
    need_zip = False
    
    def __init__(self):
        super().__init__()

    def serialize(self):
        body = struct.pack('<H', self.msg_id) + self.body
        header = struct.pack('<BIBHH', 0x1c if self.need_zip else 0xc, self.customize, 1, len(body), len(body))
        return header + body

    def deserialize(self, data):
        return data

def register_parser(msg_id: int = 0, customize: int = 0, need_zip: bool = False):
    def decorator(cls):
        class Decorator(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.msg_id = msg_id
                self.customize = customize
                self.need_zip = need_zip
        return Decorator
    return decorator