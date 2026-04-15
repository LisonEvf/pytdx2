import struct
from opentdx._typing import override

from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import exchange_board_code


@register_parser(0x122C, 1)
class BoardMembers(BaseParser):
    def __init__(
        self,
        board_symbol: str = "881001",
        sort_type=14,
        start: int = 0,
        count: int = 80,
        sort_order: bool = 1,
    ):
        # sort_order = 0 不排序,默认symbol, 不为0时候根据 sort_type 排序,sort_order = 1 升序, sort_order = 2 降序

        board_code = exchange_board_code(board_symbol)

        self.body = struct.pack("<I9x", board_code)
        # 基础参数
        params = struct.pack("<HIBBH", sort_type, start, count, 0, sort_order)
        # 额外参数, 会根据传入的值不同,返回值的数量不同. 例如只传0,则只会返回 symbol 和 symbol_name
        # pkg = bytearray.fromhex('00ff fce1 cc3f 0803 0100 0000 0000 0000 0000 0000 00')
        pkg = bytearray.fromhex("00 0000 0000 0000 0000 0000 0000 0000 0000 0000 00")

        self.body = self.body + params + pkg

    @override
    def deserialize(self, data):

        pos = 0
        header_length = 26
        header = data[:header_length]

        # 执行unpack解析
        (
            req,
            name_raw,
            total,  # 总行数标识 (4字节int)
            row_count,  # 数据类型标识 (2字节int)
        ) = struct.unpack("<16s4sIH", header)

        main_name = name_raw.decode("gbk").replace("\x00", "")
        pos += header_length
        row_lenght = 68

        stocks = []
        for i in range(row_count):
            price_pos = 0
            row_data = data[pos : pos + row_lenght]

            market, code, active1, name_raw = struct.unpack(
                "<H6s16s16s", row_data[0 : price_pos + 40]
            )

            name = name_raw.decode("gbk").replace("\x00", "")
            code = code.decode("ascii").replace("\x00", "")
            # c = 0
            # for price_i in range(base_row_lenght, row_lenght, 4):
            #     c += 1
            #     print(c, struct.unpack('<f', row_data[price_i:price_i+4])[0])

            if len(row_data) < 1:
                continue

            stocks.append(
                {
                    "name": name,
                    "market": market,
                    "symbol": code,
                }
            )

            pos += row_lenght

        result = {
            "req": req,
            "name": main_name,
            "count": row_count,
            "total": total,
            "stocks": stocks,
        }
        return result
