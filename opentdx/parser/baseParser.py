import struct

class BaseParser:
    
    msg_id = 0
    head = 0xc
    customize = 0
    need_zip = False
    body = bytearray()
    
    def __init__(self):
        super().__init__()

    def serialize(self):
        body = struct.pack('<H', self.msg_id) + self.body
        if self.head == 0xc and self.need_zip:
            self.head = 0x1c
        header = struct.pack('<BIBHH', self.head, self.customize, 1, len(body), len(body))
        return header + body

    def deserialize(self, data):
        return data

def register_parser(msg_id: int = 0, head: int = 0xc, customize: int = 0, need_zip: bool = False):
    def decorator(cls):
        cls.msg_id = msg_id
        cls.head = head
        cls.customize = customize
        cls.need_zip = need_zip
        return cls
    return decorator