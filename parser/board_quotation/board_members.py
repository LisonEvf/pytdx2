import struct
from typing import override
from parser.baseParser import BaseParser, register_parser
from utils.help import exchange_board_code
from const import BOARD_TYPE, EX_BOARD_TYPE, MARKET, EX_CATEGORY


@register_parser(0x122C, 1)
class BoardMembers(BaseParser):
    def __init__(
        self,
        board_symbol: str = "881001",
        sort_column=14,
        start: int = 0,
        page_size: int = 80,
        sort_order: bool = 1,
    ):
        # sort_column 排序字段. 14表示涨幅
        # sort_order  排序类型  0 不排序  1 降序 2升序
        board_code = exchange_board_code(board_symbol)

        self.body = struct.pack("<I9x", board_code)
        # 基础参数
        params = struct.pack("<HIBBH", sort_column, start, page_size, 0, sort_order)
        # 额外参数, 会根据传入的值不同,返回值的数量不同. 例如只传0,则只会返回 symbol 和 symbol_name
        pkg = bytearray.fromhex("00 0000 0000 0000 0000 0000 0000 0000 0000 0000 00")

        self.body = self.body + params + pkg

    @override
    def deserialize(self, data):
        header_length = 26
        row_lenght = 68

        # 执行unpack解析
        (
            req,
            name_raw,
            total,  # 总行数标识 (4字节int)
            count,  # 数据类型标识 (2字节int)
        ) = struct.unpack("<16s4sIH", data[:header_length])

        stocks = []
        for num in range(count):
            row_data = data[
                header_length + num * row_lenght : header_length
                + (num + 1) * row_lenght
            ]
            (
                market,
                code,  # 688300编号 (6字节)
                code_padding,  # 编号后填充 (18字节)
                name_raw,  # 联瑞新材GBK字节 (8字节)
                name_padding,  # 中文后填充 (30字节)
            ) = struct.unpack("<H6s16s24s20s", row_data[:68])
            name = name_raw.decode("gbk").replace("\x00", "")
            code = code.decode("gbk").replace("\x00", "")

            if market > 2:
                market_obj = EX_CATEGORY
            else:
                market_obj = MARKET

            market = market_obj(market)

            stocks.append(
                {
                    "name": name,
                    "market": market,
                    "symbol": code,
                }
            )

        result = {
            "count": count,
            "total": total,
            "stocks": stocks,
        }
        return result
