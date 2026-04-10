import struct
from typing import override

from parser.baseParser import BaseParser, register_parser
from utils.help import exchange_board_code


@register_parser(0x122C, 1)
class BoardMembersQuotes(BaseParser):
    def __init__(
        self,
        board_symbol: str = "881001",
        sort_type=14,
        start: int = 0,
        page_size: int = 80,
        sort_order: bool = 1,
    ):

        board_code = exchange_board_code(board_symbol)

        self.body = struct.pack("<I9x", board_code)
        # 基础参数
        params = struct.pack("<HIBBB", sort_type, start, page_size, 0, sort_order)
        # 额外参数, 会根据传入的值不同,返回值的数量不同. 例如只传0,则只会返回 symbol 和 symbol_name
        pkg = bytearray.fromhex("00ff fce1 cc3f 0803 01 00 0000 0000 0000 0000 0000 00")
        # pkg = bytearray.fromhex("00 0500 0000 0100 0000 00 0000 0000 0000 0000 0000 00")
        # pkg = bytearray.fromhex('0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 00')

        self.body = self.body + params + pkg
        # print(len(self.body), self.body)

    @override
    def deserialize(self, data):

        pos = 0
        header_length = 26
        header = data[:header_length]
        # print(header)

        # print("16进制: " + " ".join(f"{b:02x}" for b in header))
        # print(data)
        # 执行unpack解析
        (
            uk1,  # 固定魔数 (4字节)
            uk2,  # 名称 (16字节)
            uk3,
            uk4,
            uk5,
            uk6,
            uk7,
            uk8,
            main_name,
            total,  # 总行数标识 (4字节int)
            row_count,  # 数据类型标识 (2字节int)
        ) = struct.unpack("<HHHHHHHH4sIH", header)
        magic_num = (uk1, uk2, uk3, uk4, uk5, uk6, uk7, uk8)

        # print(header,main_name)
        pos += header_length
        row_lenght = 196

        stocks = []
        for i in range(row_count):
            price_pos = 0
            row_data = data[pos : pos + row_lenght]
            # print(len(row_data), row_data)

            market, code, active1, name_raw = struct.unpack(
                "<H6s16s16s", row_data[0 : price_pos + 40]
            )

            name = name_raw.decode("gbk").replace("\x00", "")
            price_pos += 68

            # debug
            # if int(code) == 301150:
            #     c = 0
            #     for price_i in range(68, 196, 4):
            #         c += 1
            #         print(c, struct.unpack('<f', row_data[price_i:price_i+4])[0])

            if len(row_data) < 1:
                continue

            # ========== 2. 执行unpack解析 ==========
            # 解析结果按格式符顺序赋值
            (
                market,
                code,  # 688300编号 (6字节)
                code_padding,  # 编号后填充 (18字节)
                name_raw,  # 联瑞新材GBK字节 (8字节)
                name_padding,  # 中文后填充 (30字节)
            ) = struct.unpack("<H6s16s24s20s", row_data[:68])
            name = name_raw.decode("gbk").replace("\x00", "")
            code = code.decode("gbk").replace("\x00", "")

            base_info = {"name": name, "market": market, "symbol": code}
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

            pos += row_lenght

        result = {
            "magic_num": magic_num,
            "name": main_name,
            "count": row_count,
            "total": total,
            "stocks": stocks,
        }
        return result
