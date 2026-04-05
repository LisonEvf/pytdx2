# coding=utf-8
"""
板块分析工具测试脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/lisonevf/Documents/pytdx2')

from tdx_mcp.tools.sector_analysis import (
    sector_overview,
    sector_capital_flow,
    sector_rotation_signal,
    sector_stock_correlation
)


def test_sector_overview():
    """测试板块概览"""
    print("\n📊 测试板块概览")
    print("=" * 50)
    
    # 测试行业板块
    result = sector_overview(None, 'industry')
    
    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
        return False
    
    print(f"✅ 板块类型: {result['sector_type']}")
    print(f"✅ 板块数量: {result['count']}")
    
    if result['sectors']:
        print("\n📈 Top 5 行业板块:")
        for i, sector in enumerate(result['sectors'][:5], 1):
            print(f"{i}. {sector['name']}: {sector['change_pct']:+.2f}%")
            if sector['leading_stock']:
                print(f"   领涨股: {sector['leading_stock']['name']} ({sector['leading_stock']['change_pct']:+.2f}%)")
    
    return True


def test_sector_capital_flow():
    """测试板块资金流向"""
    print("\n💰 测试板块资金流向")
    print("=" * 50)
    
    # 使用一个常见的板块代码（软件开发）
    result = sector_capital_flow(None, 'BK0428', days=5)
    
    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
        return False
    
    print(f"✅ 板块: {result['sector_name']}")
    print(f"✅ 净流入: {result['net_inflow']/100000000:.2f}亿")
    print(f"✅ 活跃股票数: {len(result['hot_stocks'])}")
    
    if result['hot_stocks']:
        print("\n🔥 活跃股票 Top 3:")
        for i, stock in enumerate(result['hot_stocks'][:3], 1):
            print(f"{i}. {stock['name']} ({stock['code']}): {stock['change_pct']:+.2f}%")
    
    return True


def test_sector_rotation_signal():
    """测试板块轮动信号"""
    print("\n🔄 测试板块轮动信号")
    print("=" * 50)
    
    result = sector_rotation_signal(None, lookback_days=5)
    
    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
        return False
    
    print(f"✅ 信号数量: {len(result['signals'])}")
    print(f"✅ 建议: {result['recommendation']}")
    
    if result['signals']:
        print("\n📊 轮动信号:")
        for i, signal in enumerate(result['signals'][:5], 1):
            print(f"{i}. {signal['sector']}: {signal['type']} (强度{signal['strength']:.1%})")
            print(f"   {signal['description']}")
    
    return True


def test_sector_stock_correlation():
    """测试个股与板块相关性"""
    print("\n🔗 测试个股与板块相关性")
    print("=" * 50)
    
    # 测试平安银行
    result = sector_stock_correlation(None, '000001', days=20)
    
    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
        return False
    
    print(f"✅ 股票: {result['stock_name']} ({result['stock_code']})")
    print(f"✅ 相关板块数: {len(result['related_sectors'])}")
    
    if result['related_sectors']:
        print("\n📊 所属板块:")
        for i, sector in enumerate(result['related_sectors'][:5], 1):
            print(f"{i}. {sector['name']} ({sector['type']})")
    
    return True


def main():
    """主测试函数"""
    print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 ")
    print("开始测试板块分析工具")
    print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 ")
    print()
    
    # 注意：这些测试需要实际的通达信连接
    # 在非交易时间或周末可能无法获取数据
    
    results = {
        '板块概览': test_sector_overview(),
        '资金流向': test_sector_capital_flow(),
        '轮动信号': test_sector_rotation_signal(),
        '板块相关性': test_sector_stock_correlation()
    }
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    # 统计
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    
    print("\n💡 提示:")
    print("- 非交易时间可能无法获取实时数据")
    print("- 周末服务器可能维护")
    print("- 请在交易时间测试完整功能")
    
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
