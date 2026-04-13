import struct
from opentdx._typing import override

from opentdx.parser.baseParser import BaseParser, register_parser
from opentdx.utils.help import exchange_board_code



def parse_row_data(row_data: bytes) -> dict:
    """
    解析单条股票数据 (196字节)
    返回包含 base_info 和 data_dict 的完整字典
    """
    # ========== 1. 解析头部 (68字节) ==========
    # 格式: <H6s16s24s20s
    # H: market (2字节)
    # 6s: code (6字节)
    # 16s: code_padding (16字节)
    # 24s: name_raw (24字节)
    # 20s: name_padding (20字节)
    header_format = "<H6s16s24s20s"
    header_size = struct.calcsize(header_format)  # = 2+6+16+24+20 = 68
    
    (
        market,
        code_bytes,
        code_padding,
        name_bytes,
        name_padding
    ) = struct.unpack(header_format, row_data[:header_size])
    
    # 解码字符串
    code = code_bytes.decode("gbk", errors="ignore").replace("\x00", "")
    name = name_bytes.decode("gbk", errors="ignore").replace("\x00", "")
    
    # TODO 添加市场信息, 在MARKET和EX_MARKET整理后, 将market进行对象化处理
    base_info = {
        "name": name,
        "market": market,
        "symbol": code
    }
    
    # ========== 2. 解析数据区 (128字节) ==========
    # 格式: <5f I 12f I f I I 3f I 2f I 2f I
    # 字段顺序:
    #   5f: pre_close, open, high, low, close
    #   I: vol
    #   12f: 量比, amount, 总股本, 流通股, 收益, 净资产收益率, uk13, 市值, PE动, zero16, zero17, 涨速
    #   I: 现量
    #   f: 换手率
    #   I: uk21
    #   I: decimal_point
    #   3f: 涨停价, 跌停价
    #   I: uk25, 每手的股数
    #   2f: 流通股2, 涨速2
    #   I: zero29
    #   2f: PE静, 市盈率TTM
    #   I: uk31
    data_format = "<5f I 9f IfI I f I I 2f 2I 2f f 2f f"
    data_size = struct.calcsize(data_format)  # = 128字节
    
    values = struct.unpack(data_format, row_data[header_size:header_size + data_size])
    
    # 字段名列表 (与上面格式对应)
    field_names = [
        "pre_close",
        "open",
        "high",
        "low",
        "close",
        "vol",
        "量比",
        "成交额",
        "总股本",
        "流通股",
        "收益",
        "净资产收益率",
        "uk13",
        "市值",
        "PE动",
        "zero16", #港股才有数值
        "zero17", #港股才有
        "涨速",
        "现量",
        "换手率",
        "uk21",
        "decimal_point",
        "涨停价",
        "跌停价",
        "uk25",
        "每手股数",
        "流通股/PE",
        "涨速2",
        "zero29",
        "PE静",
        "市盈率TTM",
        "uk31",
    ]
    
    # 创建数据字典
    data_dict = dict(zip(field_names, values))
    
    # ========== 3. 合并返回 ==========
    return {**base_info, **data_dict}


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

        print(f"16进制: {header.hex()} totol: {total} count:{row_count}")
        pos += header_length
        row_lenght = 196

        stocks = []
        for i in range(row_count):
            row_data = data[pos + i * row_lenght : pos + (i + 1) * row_lenght]
            stock_dict = parse_row_data(row_data)
            stocks.append(stock_dict)

        result = {
            "magic_num": magic_num,
            "name": main_name,
            "count": row_count,
            "total": total,
            "stocks": stocks,
        }
        return result