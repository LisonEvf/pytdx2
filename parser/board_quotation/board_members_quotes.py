import struct
from typing import override
from parser.base_parser import BaseParser, register_parser
from utils.help import exchange_board_code
from const import BOARD_TYPE, EX_BOARD_TYPE, MARKET, EX_CATEGORY


@register_parser(0x122C, 1)
class BoardMembersQuotes(BaseParser):
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
        pkg = bytearray.fromhex("00ff fce1 cc3f 0803 0100 0000 0000 0000 0000 0000 00")

        self.body = self.body + params + pkg

    @override
    def deserialize(self, data):
        header_length = 26
        row_lenght = 196

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
            market, code, uk3, name_raw = struct.unpack("<H6s16s16s", row_data[0:40])
            name = name_raw.decode("gbk").replace("\x00", "")
            code = code.decode("ascii").replace("\x00", "")

            # 建议market 在外部进行 对象化处理
            if market > 2:
                market_obj = EX_CATEGORY
            else:
                market_obj = MARKET

            base_info = {"name": name, "market": market_obj(market), "symbol": code}
            # 定义字段名列表
            field_names = [
                "pre_close",
                "open",
                "high",
                "low",
                "close",
                "uk6",
                "量比",
                "成交额",
                "总股本",  # 单位万
                "流通股",  # 单位万
                "收益",
                "净资产收益率",
                "uk13",
                "市值",
                "PE动",
                "zero16",
                "zero17",
                "涨速",
                "现量",
                # "uk19",
                "换手率",
                "uk21",
                "uk22",
                "涨停价",
                "跌停价",
                "zero25",
                "uk26",
                "uk27",  # 疑似昨日 PE静
                "涨速2",
                "zero29",
                "PE静",
                "市盈率TTM",
                "uk31 ",
            ]

            # 解包并创建字典
            values = struct.unpack("<18fH2x13f", row_data[68 : 68 + 32 * 4])
            data_dict = dict(zip(field_names, values))

            combined_dict = {**base_info, **data_dict}

            stocks.append(combined_dict)

        result = {
            "count": count,
            "total": total,
            "stocks": stocks,
        }
        return result
