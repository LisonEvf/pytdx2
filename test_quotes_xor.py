#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 QuotesXor 解析器

使用用户提供的 hex 数据验证解析结果
"""

import struct

# 用户提供的原始 hex 数据
HEX_DATA = (
    "949392aaaaaaaaaaaaf19a0b5fbc7f9c4cda3c974cda5f2a92932a92256804429193670377c1017c7e37922b1f393f92332c39c210534d902e42608193068b1d98304e0c91001d8a88912e1916db931486139c9393939393939393919393939393939393934b5fbc4b5fbc93934b5fbc4b5fbc93934b5fbc4b5fbc93934b5fbc4b5fbc93934b5fbc4b5fbc93934b5fbc4b5fbc939393a0aaaaa3a3a2f09a214334927d57927071900d92547a90f82a929306911979616d913d0dc130da84c0155928279232332459923b1620f82727189e0f62019a933db30c98341b629293b69218547496931988238293939393939393939193362060939393939361433492614334929393614334926143349293936143349261433492939361433492614334929393614334926143349293936143349261433492939391abaaaaa3a6a31c9613299c1f92718b09905588eb2a9293bd216a6a91070792a8932ddc1f3f5292305e2b92161013922975099293933391109193939393939332911f9193939393939393939193939393939393939353299c53299c939353299c53299c939353299c53299c939353299c53299c939353299c53299c939353299c53299c939393a0aaaaa3a3a5f09a3630bb47b963f13e925ffcf82a929314911d1b2ef0163db100ae12c10b5951bd192d69a73f1407b837070090939336832197939391939393119e399b93939393939393939193d256a693939393937630bb7630bb93937630bb7630bb93937630bb7630bb93937630bb7630bb93937630bb7630bb93937630bb7630bb939392a3a3a3a5ababf19a217b9c52984abc21924abcf82a9293a9161458971e5892457e7bc31a3e079a1b0765990d6d47951b4d0c9293933d9438929393939393931b960097939393939393939391939393939393939393617b9c617b9c9393617b9c617b9c9393617b9c617b9c9393617b9c617b9c9393617b9c617b9c9393617b9c617b9c939392a3a3a3a0a3a3f09a0363a5548f51f7189759f7fd2a9293cc102844fd3c4e95756ee7c12b2749b4134a17b4334a34bd09253797939338912a929393939393930e9232929393939393939393919393939393939393934363a54363a593934363a54363a593934363a54363a593934363a54363a593934363a54363a593934363a54363a5939392ababa3a3a3a6b1993f03bd735f9f5b05883f6487773fbfe22a929393275c7241963060921e1016c00492249713654f2e923b5a2e9293932ea11e8593932497049293930e928d939321929c9393139290919393939393939393937f03bd7f03bd93937f03bd7f03bd93937f03bd7f03bd93937f03bd7f03bd93937f03bd7f03bd93937f03bd7f03bd9393"
)

DECODE_KEY = 0x93


def decode_byte(b: int) -> int:
    """解码单个字节: 结果 = 编码 XOR 0x93"""
    return b ^ DECODE_KEY


def decode_data(data: bytes) -> bytes:
    """解码整个数据块"""
    return bytes([decode_byte(b) for b in data])


def get_price(data: bytes, pos: int) -> tuple[int, int]:
    """解析变长编码的价格数据"""
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


def test_basic_decode():
    """测试基础解码"""
    print("=" * 60)
    print("测试1: XOR 0x93 解码验证")
    print("=" * 60)

    data = bytes.fromhex(HEX_DATA)
    decoded = decode_data(data)

    print(f"原始数据长度: {len(data)} 字节")
    print(f"解码后前30字节: {decoded[:30].hex()}")

    # 解析 count
    count = struct.unpack('<H', decoded[:2])[0]
    print(f"\n记录数: {count}")

    # 验证解码公式
    print(f"\n解码公式验证:")
    print(f"  0x94 XOR 0x93 = 0x{0x94 ^ 0x93:02x} (期望: 0x07)")
    print(f"  0xaa XOR 0x93 = 0x{0xaa ^ 0x93:02x} = '{chr(0xaa ^ 0x93)}'")

    return decoded, count


def test_find_records(decoded: bytes, count: int):
    """测试记录定位和解析"""
    print("\n" + "=" * 60)
    print("测试2: 记录定位与解析")
    print("=" * 60)

    # 已知的分隔符位置 (从原始数据分析得出)
    # 分隔符在编码数据中的位置
    data = bytes.fromhex(HEX_DATA)
    sep_positions = [149, 312, 581, 715, 849]

    # 构建记录范围
    record_ranges = []
    start = 2
    for sep in sep_positions:
        record_ranges.append((start, sep))
        start = sep  # 分隔符本身就是下一条记录的头部
    if start < len(decoded):
        record_ranges.append((start, len(decoded)))

    print(f"找到 {len(record_ranges)} 条记录\n")

    results = []
    for i, (rec_start, rec_end) in enumerate(record_ranges[:count]):
        result = parse_record(decoded, rec_start, rec_end)
        if result:
            results.append(result)
            print(f"记录 {i+1}:")
            print(f"  市场: {result['market_name']} ({result['market']})")
            print(f"  代码: {result['code']}")
            print(f"  成交量: {result['vol']:,}")
            print(f"  成交额: {result['amount']:,.2f}")
            print(f"  内盘: {result['in_vol']:,}")
            print(f"  外盘: {result['out_vol']:,}")
            print()

    return results


def parse_record(decoded: bytes, start: int, end: int) -> dict | None:
    """解析单条记录"""
    if end - start < 20:
        return None

    pos = start

    # 头部: 市场(1) + 代码(6)
    market = decoded[pos]
    code_bytes = decoded[pos + 1:pos + 7]
    pos += 7

    # 解析代码
    try:
        if all(0x30 <= b <= 0x39 for b in code_bytes):
            code = code_bytes.decode('ascii')
        else:
            code = code_bytes.decode('latin-1').strip('\x00')
    except:
        code = code_bytes.hex()

    market_names = {0: '深圳', 1: '上海', 2: '北京'}

    try:
        # 价格数据
        price_delta, pos = get_price(decoded, pos)
        pre_close_delta, pos = get_price(decoded, pos)
        open_delta, pos = get_price(decoded, pos)
        high_delta, pos = get_price(decoded, pos)
        low_delta, pos = get_price(decoded, pos)
        server_time, pos = get_price(decoded, pos)
        neg_price, pos = get_price(decoded, pos)
        vol, pos = get_price(decoded, pos)
        cur_vol, pos = get_price(decoded, pos)

        # 成交额
        if pos + 4 <= end:
            amount = struct.unpack('<f', decoded[pos:pos + 4])[0]
            pos += 4
        else:
            amount = 0.0

        # 内外盘
        in_vol, pos = get_price(decoded, pos) if pos < end else (0, pos)
        out_vol, pos = get_price(decoded, pos) if pos < end else (0, pos)

        return {
            'market': market,
            'market_name': market_names.get(market, f'未知({market})'),
            'code': code,
            'price_delta': price_delta,
            'vol': vol,
            'amount': amount,
            'in_vol': in_vol,
            'out_vol': out_vol,
            'server_time': server_time,
        }

    except Exception as e:
        return None


def test_parser_class():
    """测试 QuotesXor 解析器类"""
    print("=" * 60)
    print("测试3: QuotesXor 解析器类")
    print("=" * 60)

    from tdx_mcp.parser.quotation.stock import QuotesXor
    from tdx_mcp.const import MARKET

    # 创建解析器实例
    parser = QuotesXor([(MARKET.SH, '999999')])

    # 使用原始数据进行反序列化
    data = bytes.fromhex(HEX_DATA)
    results = parser.deserialize(data)

    market_names = {MARKET.SH: '上海', MARKET.SZ: '深圳', MARKET.BJ: '北京'}

    print(f"解析到 {len(results)} 条记录:\n")
    for i, rec in enumerate(results):
        print(f"记录 {i+1}:")
        print(f"  市场: {market_names.get(rec['market'], rec['market'])}")
        print(f"  代码: {rec['code']}")
        print(f"  价格: {rec['price']/1000:.2f}")
        print(f"  成交额: {rec['amount']:,.0f} 元 ({rec['amount']/100000000:.2f}亿)")
        print(f"  外盘: {rec['out_vol']:,}")
        print(f"  内盘: {rec['in_vol']:,}")
        print()

    return results


def main():
    print("QuotesXor 解析器验证测试\n")

    # 测试1: 基础解码
    decoded, count = test_basic_decode()

    # 测试2: 记录解析
    records = test_find_records(decoded, count)

    # 测试3: 解析器类
    try:
        class_results = test_parser_class()
    except Exception as e:
        print(f"解析器类测试失败: {e}")

    print("=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
