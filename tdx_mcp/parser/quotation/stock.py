from tdx_mcp.parser.quotation.auction import Auction
from tdx_mcp.parser.quotation.board_list import BoardList
from tdx_mcp.parser.quotation.chart_sampling import ChartSampling
from tdx_mcp.parser.quotation.count import Count
from tdx_mcp.parser.quotation.history_orders import HistoryOrders
from tdx_mcp.parser.quotation.history_tick_chart import HistoryTickChart
from tdx_mcp.parser.quotation.history_transaction_with_trans import HistoryTransactionWithTrans
from tdx_mcp.parser.quotation.history_transaction import HistoryTransaction
from tdx_mcp.parser.quotation.index_info import IndexInfo
from tdx_mcp.parser.quotation.index_momentum import IndexMomentum
from tdx_mcp.parser.quotation.kline_offset import K_Line_Offset
from tdx_mcp.parser.quotation.kline import K_Line
from tdx_mcp.parser.quotation.list import List
from tdx_mcp.parser.quotation.list2 import List2
from tdx_mcp.parser.quotation.quotes_detail import QuotesDetail
from tdx_mcp.parser.quotation.quotes_list import QuotesList
from tdx_mcp.parser.quotation.quotes import Quotes
from tdx_mcp.parser.quotation.tick_chart import TickChart
from tdx_mcp.parser.quotation.top_board import TopBoard
from tdx_mcp.parser.quotation.transaction import Transaction
from tdx_mcp.parser.quotation.unusual import Unusual
from tdx_mcp.parser.quotation.volume_profile import VolumeProfile

__all__ = [
    'Auction',
    'BoardList',
    'ChartSampling',
    'Count',
    'HistoryOrders',
    'HistoryTickChart',
    'HistoryTransactionWithTrans',
    'HistoryTransaction',
    'IndexInfo',
    'IndexMomentum',
    'K_Line_Offset',
    'K_Line',
    'List',
    'List2',
    'QuotesDetail',
    'QuotesList',
    'Quotes',
    'QuotesXor',
    'TickChart',
    'TopBoard',
    'Transaction',
    'Unusual',
    'VolumeProfile',
    'f452',
]

from tdx_mcp.const import MARKET
from tdx_mcp.parser.baseParser import BaseParser, register_parser
import struct
from typing import override


    
@register_parser(0x452)
class f452(BaseParser):
    def __init__(self, start:int = 0, count:int = 2000):
        self.body = struct.pack('<IIIH', start, count, 1, 0)

    @override
    def deserialize(self, data):
        count, = struct.unpack('<H', data[:2])
        result = []
        for i in range(count):
            market, code_num, p1, p2 = struct.unpack('<BIff', data[i * 13 + 2: i * 13 + 15])
            result.append({
                'market': MARKET(market),
                'code': f'{code_num}',
                'p1': p1,
                'p2': p2
            })

        return result
    

# >0700
# 01 393939393939 c437 0200 # 01 393939393939 e355 0200
# 00 333939303031 c437 0200 # 00 333939303031 ae55 0200
# 02 383939303530 bf37 0200 # 02 383939303530 aa55 0200
# 00 333939303036 c437 0200 # 00 333939303036 554a 0200
# 01 303030363838 c437 0200 # 01 303030363838 f949 0200
# 01 303030333030 c437 0200 # 01 303030333030 f949 0200
# 01 383830303035 c337 0200 # 01 383830303035 b055 0200

# < 9493
# 92aaaaaaaaaaaa
# 1f812b7bbc50b941891a97478970c69193d9233a48619093b572a4c0054d18669229585c6e9213365ad20c7a4e900d5a3a8d9334800f9c0c7701973b5a91bd953a083e7d9293089d289c939393939393939391939393939393939393
# 6b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc93936b7bbc6b7bbc9393
# 
# 93a0aaaaa3a3a2
# 1e810a733192603f917e3492308a7e34923dc69193b01c6a317c97938830eac0151721249139666324912b6f6afd1f005c9f3f02329e930c8a1881077f7f9793a8910d5c048e933e83399c93939393939393939193900ae39293939393
# 4a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a73319293934a7331924a7331929393
# 
# 91abaaaaa3a6a3
# 9b98334b824b962d92299e429e3ac691932692222b429a93af160bc3311a6c972e2d419713224f923c6f239293930791179193939293939334912592939393939393939391939393939393939393
# 734b82734b829393734b82734b829393734b82734b829393734b82734b829393734b82734b829393734b82734b829393
# 
# 93a0aaaaa3a3a5
# 1e810d68b56cff63a8009a63a860da9193b42b29733c921c1957aa6ff270c103382ac4251c34cb2b535dba3c796c919393009f3e9b939395929393069a199b939393939393939391935d48c29393939393
# 4d68b54d68b593934d68b54d68b593934d68b54d68b593934d68b54d68b593934d68b54d68b593934c68b54c68b59393
# 
# 92a3a3a3a5abab
# 188106358379ba55b2329755b26ada9193903d7841942d1cfac7fbdec2247004821e0e49821f4f6692013f329293932296049093939293939316971797939393939393939391939393939393939393
# 463583463583939346358346358393934635834635839393463583463583939346358346358393934635834635839393
# 
# 92a3a3a3a0a3a3
# 1f813936ab6bd048b63a9548b66ada919354922b285f0e920b421192e12943c1271614a0290840a6176235b2240c229793930691189193939193939314923592939393939393939391939393939393939393
# 7936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab93937936ab7936ab9393
# 
# 92ababa3a3a3a6
# d5803325b74718904f709b2b0c8d6716b13ec6919393355001789b030097498e48c037923897230f0e21923b2d0791939307b628b3939338973792939313918e93933a918e93933a929b91939393939393939393
# 7325b77325b793937325b77325b793937325b77325b793937325b77325b793937325b77325b793937325b77325b79393

# 93 -> 0  -> a3
# 92 -> 1  -> a2
# 91 -> 2  -> a1
# 90 -> 3  -> a0
# 97 -> 4  -> a7
# 96 -> 5  -> a6
# 95 -> 6  -> a5
# 94 -> 7  -> a4
# 9b -> 8  -> ab
# 9a -> 9  -> aa
# 99 -> 10
# 98 -> 11
# 9f -> 12
# 9e -> 13
# 9d -> 14
# 9c -> 15
# 83 -> 16
# 82 -> 17
# 81 -> 18
@register_parser(0x547)
class QuotesXor(BaseParser):
    """
    0x547协议解析器 - 使用XOR 0x93编码的行情数据

    编码规则: 编码字节 XOR 0x93 = 解码值
    数据结构: count(2字节) + [记录数据] * count
    每条记录: 市场(1) + 代码(6) + 价格数据(变长) + 其他字段

    记录边界: 下一条记录的头部(市场+代码)就是分隔符
    """

    DECODE_KEY = 0x93

    def __init__(self, stocks: list[tuple[MARKET, str]]):
        count = len(stocks)
        if count <= 0:
            raise Exception('stocks count must > 0')
        self.body = bytearray(struct.pack('<H', count))

        for market, code in stocks:
            self.body.extend(struct.pack('<B6sHH', market.value, code.encode('gbk'), 22234, 2))

    def _decode_byte(self, b: int) -> int:
        """解码单个字节: 结果 = 编码 XOR 0x93"""
        return b ^ self.DECODE_KEY

    def _decode_data(self, data: bytes) -> bytes:
        """解码整个数据块"""
        return bytes([self._decode_byte(b) for b in data])

    def _get_price(self, data: bytes, pos: int) -> tuple[int, int]:
        """
        解析变长编码的价格数据
        返回: (价格值, 新位置)
        """
        pos_byte = 6
        bdata = data[pos]
        int_data = bdata & 0x3f
        sign = bool(bdata & 0x40)

        if bdata & 0x80:
            while True:
                pos += 1
                if pos >= len(data):
                    break
                bdata = data[pos]
                int_data += (bdata & 0x7f) << pos_byte
                pos_byte += 7
                if not (bdata & 0x80):
                    break

        pos += 1
        if sign:
            int_data = -int_data

        return int_data, pos

    def _find_record_boundaries(self, data: bytes, decoded: bytes, count: int) -> list[tuple[int, int]]:
        """
        找到记录边界

        方法: 在原始编码数据中查找下一条记录头部的编码模式
        头部编码特征: 市场代码(0/1/2) XOR 0x93 后面跟着代码的编码
        """
        boundaries = []

        # 方法1: 在编码数据中查找已知的分隔符模式
        # 编码后的分隔符模式 (市场代码 + 代码前几字节)
        sep_patterns = [
            bytes([0x93, 0xa0, 0xaa, 0xaa, 0xa3]),  # 市场0开头
            bytes([0x91, 0xab, 0xaa, 0xaa, 0xa3]),  # 市场2开头
            bytes([0x92, 0xa3, 0xa3, 0xa3]),        # 市场1, 代码000开头
            bytes([0x92, 0xab, 0xab, 0xa3]),        # 市场1, 代码88开头
        ]

        sep_positions = []
        for pattern in sep_patterns:
            pos = 0
            while True:
                idx = data.find(pattern, pos)
                if idx < 0:
                    break
                if idx > 10:  # 跳过开头的误判
                    sep_positions.append(idx)
                pos = idx + 1

        sep_positions.sort()

        # 构建记录范围
        start = 2  # 跳过count
        for sep_pos in sep_positions[:count-1]:  # 最多count-1个分隔符
            boundaries.append((start, sep_pos))
            start = sep_pos  # 分隔符本身就是下一条记录的头部

        # 最后一条记录
        if start < len(decoded):
            boundaries.append((start, len(decoded)))

        return boundaries

    @override
    def deserialize(self, data: bytes) -> list[dict]:
        """
        反序列化响应数据

        返回格式:
        [
            {
                'market': MARKET,
                'code': str,
                'price_delta': int,  # 价格偏移 (相对于基准价)
                'vol': int,          # 成交量
                'amount': float,     # 成交额
                'in_vol': int,       # 内盘
                'out_vol': int,      # 外盘
                ...
            },
            ...
        ]
        """
        # 1. 先对整个数据进行XOR解码
        decoded = self._decode_data(data)

        # 2. 解析记录数
        count = struct.unpack('<H', decoded[:2])[0]

        # 3. 找到记录边界
        boundaries = self._find_record_boundaries(data, decoded, count)

        # 4. 解析每条记录
        results = []
        for rec_start, rec_end in boundaries[:count]:
            try:
                record = self._parse_record(decoded, rec_start, rec_end)
                if record:
                    results.append(record)
            except Exception:
                continue

        return results

    def _parse_record(self, decoded: bytes, start: int, end: int) -> dict | None:
        """
        解析单条记录

        0x547协议数据结构 (通过分析实际数据确定):
        - 头部: market(1) + code(6) + active(2) = 9字节
        - 字段1-6: 变长编码 (价格相关)
        - 分隔符: 121 和 0 (顺序可能变化)
        - 成交额: 变长编码, 单位:元
        - 外盘, 内盘等...
        """
        if end - start < 30:
            return None

        pos = start

        # 头部: 市场(1) + 代码(6) + active(2)
        market = decoded[pos]
        code_bytes = decoded[pos + 1:pos + 7]
        active = struct.unpack('<H', decoded[pos + 7:pos + 9])[0]
        pos += 9

        # 解析代码
        try:
            if all(0x30 <= b <= 0x39 for b in code_bytes):
                code = code_bytes.decode('ascii')
            else:
                code = code_bytes.decode('latin-1').strip('\x00')
        except:
            code = code_bytes.hex()

        try:
            # 字段1-6: 价格相关
            price, pos = self._get_price(decoded, pos)
            pre_close, pos = self._get_price(decoded, pos)
            open_delta, pos = self._get_price(decoded, pos)
            high_delta, pos = self._get_price(decoded, pos)
            low_delta, pos = self._get_price(decoded, pos)
            vol, pos = self._get_price(decoded, pos)

            # 跳过分隔符 (121 和 0，顺序可能变化)
            # 找到成交额位置 (通常在分隔符后)
            amount = 0
            out_vol = 0
            in_vol = 0

            # 扫描后续字段，找到合理的成交额 (100万-10000亿)
            for _ in range(10):
                if pos >= end - 2:
                    break
                val, pos = self._get_price(decoded, pos)
                if 100_000_000 < val < 10_000_000_000_000:
                    amount = val
                    # 成交额后的字段: 外盘, 内盘
                    if pos < end:
                        out_vol, pos = self._get_price(decoded, pos)
                    if pos < end:
                        in_vol, pos = self._get_price(decoded, pos)
                    break

            return {
                'market': MARKET(market) if market in [0, 1, 2] else market,
                'code': code,
                'active': active,
                'price': price,
                'pre_close': price + pre_close,
                'open': price + open_delta,
                'high': price + high_delta,
                'low': price + low_delta,
                'vol': vol,
                'amount': amount,  # 成交额 (元)
                'out_vol': out_vol,
                'in_vol': in_vol,
            }

        except Exception:
            return None