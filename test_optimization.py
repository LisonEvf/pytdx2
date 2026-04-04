#!/usr/bin/env python3
# coding=utf-8
"""
性能优化测试脚本

测试优化后的工具性能提升
"""

import time
from tdx_mcp.client.quotationClient import QuotationClient
from tdx_mcp.tools.market_analysis import market_overview, market_breadth, sector_rotation
from tdx_mcp.tools.stock_analysis import stock_detail, capital_flow


def test_performance():
    """测试优化后的性能"""
    client = QuotationClient(True, True)
    client.connect().login()
    
    print("📊 性能优化测试开始\n")
    print("=" * 60)
    
    # 测试1: market_overview（采样量从300降至150）
    print("\n【测试1】market_overview（优化采样）")
    start = time.time()
    result1 = market_overview(client)
    elapsed1 = time.time() - start
    print(f"✅ 耗时: {elapsed1:.2f}秒")
    print(f"   指数数量: {len(result1.get('indices', []))}")
    print(f"   样本数: {result1.get('breadth', {}).get('sample_count', 'N/A')}")
    
    # 测试2: market_breadth（优化后使用A股分类）
    print("\n【测试2】market_breadth（优化分类）")
    start = time.time()
    result2 = market_breadth(client)
    elapsed2 = time.time() - start
    print(f"✅ 耗时: {elapsed2:.2f}秒")
    print(f"   上涨: {result2.get('up', 0)}, 下跌: {result2.get('down', 0)}")
    print(f"   样本数: {result2.get('sample_count', 'N/A')}")
    
    # 测试3: sector_rotation
    print("\n【测试3】sector_rotation")
    start = time.time()
    result3 = sector_rotation(client)
    elapsed3 = time.time() - start
    print(f"✅ 耗时: {elapsed3:.2f}秒")
    print(f"   领涨板块: {len(result3.get('top_gainers', []))}")
    
    # 测试4: stock_detail（个股详情）
    print("\n【测试4】stock_detail（000001平安银行）")
    start = time.time()
    result4 = stock_detail(client, MARKET.SZ, '000001')
    elapsed4 = time.time() - start
    print(f"✅ 耗时: {elapsed4:.2f}秒")
    if 'basic' in result4:
        print(f"   股票: {result4['basic'].get('name', 'N/A')}")
        print(f"   市盈率: {result4['quote'].get('pe_ratio', 'N/A')}")
    
    # 测试5: capital_flow（资金流向）
    print("\n【测试5】capital_flow（000001平安银行）")
    start = time.time()
    result5 = capital_flow(client, MARKET.SZ, '000001')
    elapsed5 = time.time() - start
    print(f"✅ 耗时: {elapsed5:.2f}秒")
    print(f"   主力净流入: {result5.get('main_net_inflow', 0) / 10000:.2f}万")
    print(f"   评估: {result5.get('assessment', 'N/A')}")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 性能总结:")
    print(f"  market_overview: {elapsed1:.2f}秒（预期<2秒）")
    print(f"  market_breadth: {elapsed2:.2f}秒（预期<2秒）")
    print(f"  sector_rotation: {elapsed3:.2f}秒（预期<1秒）")
    print(f"  stock_detail: {elapsed4:.2f}秒（预期<1秒）")
    print(f"  capital_flow: {elapsed5:.2f}秒（预期<1秒）")
    
    total_time = elapsed1 + elapsed2 + elapsed3 + elapsed4 + elapsed5
    print(f"\n  总耗时: {total_time:.2f}秒")
    print(f"  平均耗时: {total_time / 5:.2f}秒/工具")
    
    # 性能评估
    if total_time < 10:
        print("\n✅ 性能优秀（总耗时<10秒）")
    elif total_time < 20:
        print("\n⚠️ 性能良好（总耗时10-20秒）")
    else:
        print("\n❌ 性能需优化（总耗时>20秒）")
    
    client.disconnect()


if __name__ == '__main__':
    test_performance()
