"""测试新增的 mac_quotation 解析器 - 验证请求体格式并发送到服务器捕获响应"""
import struct
from opentdx.const import MARKET
from opentdx.parser.mac_quotation import (
    ServerInit, FileList, FileDownload, StockQuery,
    BatchStockData, StockDetail, StockBarCount,
    StockSmallInfo, KlineOffset,
)
from opentdx.client.MacQuotationClient import MacQuotationClient


def verify_bodies():
    """验证请求体格式是否与 proto.txt 一致"""
    # proto.txt 中的预期数据
    proto = {
        '0x120F': '04002d3100000000000000000027060e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
        '0x1215': '00000000697773686f702f305f3030323933382e68746d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
        '0x1217': '010000000000000030750000697773686f702f305f3030323933382e68746d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
        '0x122A': '00003030323933380000000000000000000000000000000001000000000500000000000000000000',
        '0x122B': 'ffffffffff58ff070000000200000000000000000100010036383838313300000000000000000000000000000000',
        '0x122F': '0000303032393338000000000000000000000000000000000000000000000000320001000000000000000000',
        '0x123D': '00003030323933380000000000000000000000000000000000000000f401000000000000000000000000',
        '0x123E': '0100363838383133000000000000000000000000000000000000000005000100000000000000',
        '0x124A': '0000000000f401000000000000',
    }

    parsers = [
        ('0x120F', ServerInit()),
        ('0x1215', FileList('iwshop/0_002938.htm')),
        ('0x1217', FileDownload('iwshop/0_002938.htm')),
        ('0x122A', StockQuery(MARKET.SZ, '002938', flag=1, unk=5)),
        ('0x122B', BatchStockData(MARKET.SH, '688813')),
        ('0x122F', StockDetail(MARKET.SZ, '002938')),
        ('0x123D', StockBarCount(MARKET.SZ, '002938')),
        ('0x123E', StockSmallInfo(MARKET.SH, '688813')),
        ('0x124A', KlineOffset()),
    ]

    all_pass = True
    for name, parser in parsers:
        body_hex = parser.body.hex()
        expected = proto[name]
        match = body_hex == expected
        status = "PASS" if match else "FAIL"
        if not match:
            all_pass = False
            print(f"[{status}] {name} ({len(parser.body)}B)")
            # 找到差异位置
            for i in range(min(len(body_hex), len(expected))):
                if body_hex[i] != expected[i]:
                    print(f"  diff at pos {i}: got {body_hex[i]}, expected {expected[i]}")
                    print(f"  got:      ...{body_hex[max(0,i-5):i+20]}...")
                    print(f"  expected: ...{expected[max(0,i-5):i+20]}...")
                    break
        else:
            print(f"[{status}] {name} ({len(parser.body)}B)")

    return all_pass


def capture_responses():
    """发送每个解析器请求并捕获服务器响应"""
    client = MacQuotationClient()
    if not client.connect():
        print("连接服务器失败!")
        return

    test_cases = [
        ("0x120F ServerInit", ServerInit()),
        ("0x1215 FileList", FileList("tdxbase/hspy.dat")),
        ("0x1217 FileDownload", FileDownload("tdxbase/hspy.dat")),
        ("0x122A StockQuery SZ", StockQuery(MARKET.SZ, "002938")),
        ("0x122A StockQuery SH", StockQuery(MARKET.SH, "688813")),
        ("0x122B BatchStock SH", BatchStockData(MARKET.SH, "688813")),
        ("0x122B BatchStock SZ", BatchStockData(MARKET.SZ, "002938")),
        ("0x122F StockDetail SZ", StockDetail(MARKET.SZ, "002938")),
        ("0x122F StockDetail SH", StockDetail(MARKET.SH, "688813")),
        ("0x123D StockBarCount SZ", StockBarCount(MARKET.SZ, "002938")),
        ("0x123D StockBarCount SH", StockBarCount(MARKET.SH, "688813")),
        ("0x123E StockSmallInfo", StockSmallInfo(MARKET.SH, "688813")),
        ("0x124A KlineOffset 0", KlineOffset(0)),
        ("0x124A KlineOffset 128000", KlineOffset(128000)),
    ]

    for name, parser in test_cases:
        try:
            print(f"\n{'='*60}")
            print(f"Testing: {name}")
            response = client.call(parser)
            if response is not None:
                if isinstance(response, bytes):
                    # 显示前 200 字节的 hex 和总长度
                    hex_str = response.hex()
                    print(f"Response ({len(response)} bytes): {hex_str[:400]}")
                    if len(hex_str) > 400:
                        print(f"  ... ({len(hex_str)//2} total bytes)")
                else:
                    print(f"Response: {response}")
            else:
                print("Response: None")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

    client.disconnect()


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1: 验证请求体格式")
    print("=" * 60)
    if verify_bodies():
        print("\n全部通过!")
    else:
        print("\n有格式不匹配!")

    print("\n" + "=" * 60)
    print("Phase 2: 发送请求并捕获响应")
    print("=" * 60)
    capture_responses()
