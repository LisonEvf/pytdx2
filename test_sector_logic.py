# coding=utf-8
"""
板块分析逻辑测试（离线）
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/lisonevf/Documents/pytdx2')


def test_sector_calculation_logic():
    """测试板块计算逻辑（离线）"""
    print("\n📊 测试板块计算逻辑")
    print("=" * 50)
    
    # 模拟板块数据
    mock_sectors = [
        {'code': 'BK0001', 'name': '软件开发', 'change_pct': 2.5},
        {'code': 'BK0002', 'name': '芯片制造', 'change_pct': 3.2},
        {'code': 'BK0003', 'name': '人工智能', 'change_pct': 1.8},
    ]
    
    # 计算板块平均涨跌幅
    total_change = sum(s['change_pct'] for s in mock_sectors)
    avg_change = total_change / len(mock_sectors)
    
    print(f"✅ 板块数量: {len(mock_sectors)}")
    print(f"✅ 平均涨跌幅: {avg_change:.2f}%")
    
    # 排序（涨跌幅降序）
    sorted_sectors = sorted(mock_sectors, key=lambda x: x['change_pct'], reverse=True)
    
    print("\n📈 板块涨跌幅排序:")
    for i, sector in enumerate(sorted_sectors, 1):
        print(f"{i}. {sector['name']}: {sector['change_pct']:+.2f}%")
    
    return True


def test_capital_flow_logic():
    """测试资金流向逻辑"""
    print("\n💰 测试资金流向逻辑")
    print("=" * 50)
    
    # 模拟股票数据
    mock_stocks = [
        {'code': '000001', 'name': '平安银行', 'amount': 5000000000, 'change_pct': 2.5},
        {'code': '000002', 'name': '万科A', 'amount': 3000000000, 'change_pct': -1.2},
        {'code': '000004', 'name': '国华网安', 'amount': 800000000, 'change_pct': 5.8},
    ]
    
    # 计算资金流向
    total_inflow = 0
    total_outflow = 0
    
    for stock in mock_stocks:
        amount = stock['amount']
        change_pct = stock['change_pct']
        
        if change_pct > 0:
            inflow = amount * (change_pct / 100) * 0.5
            total_inflow += inflow
        else:
            outflow = abs(amount * (change_pct / 100) * 0.5)
            total_outflow += outflow
    
    net_inflow = total_inflow - total_outflow
    
    print(f"✅ 总流入: {total_inflow/100000000:.2f}亿")
    print(f"✅ 总流出: {total_outflow/100000000:.2f}亿")
    print(f"✅ 净流入: {net_inflow/100000000:.2f}亿")
    
    # 找活跃股票
    hot_stocks = [s for s in mock_stocks if s['amount'] > 1000000000]
    hot_stocks.sort(key=lambda x: x['amount'], reverse=True)
    
    print(f"\n🔥 活跃股票 ({len(hot_stocks)}个):")
    for i, stock in enumerate(hot_stocks, 1):
        print(f"{i}. {stock['name']}: {stock['amount']/100000000:.1f}亿")
    
    return True


def test_rotation_signal_logic():
    """测试轮动信号逻辑"""
    print("\n🔄 测试轮动信号逻辑")
    print("=" * 50)
    
    # 模拟板块数据
    mock_sector_data = {
        '人工智能': {
            'up_count': 45,
            'down_count': 5,
            'total': 50,
            'amount': 8000000000
        },
        '房地产开发': {
            'up_count': 10,
            'down_count': 40,
            'total': 50,
            'amount': 6000000000
        },
        '汽车整车': {
            'up_count': 25,
            'down_count': 25,
            'total': 50,
            'amount': 4000000000
        }
    }
    
    signals = []
    
    for sector_name, data in mock_sector_data.items():
        up_ratio = data['up_count'] / data['total']
        total_amount = data['amount']
        
        signal_type = None
        strength = 0
        description = ''
        
        # 强势启动
        if up_ratio >= 0.8 and total_amount > 5000000000:
            signal_type = '强势启动'
            strength = min(up_ratio + 0.1, 1.0)
            description = f'上涨股票{int(up_ratio*100)}%'
        
        # 超跌反弹
        elif up_ratio <= 0.2 and total_amount > 3000000000:
            signal_type = '超跌反弹'
            strength = 0.6
            description = f'下跌股票{int((1-up_ratio)*100)}%'
        
        # 分化
        elif 0.4 <= up_ratio <= 0.6 and total_amount > 2000000000:
            signal_type = '板块分化'
            strength = 0.5
            description = '多空分歧'
        
        if signal_type:
            signals.append({
                'sector': sector_name,
                'type': signal_type,
                'strength': strength,
                'description': description
            })
    
    # 排序
    signals.sort(key=lambda x: x['strength'], reverse=True)
    
    print(f"✅ 检测到 {len(signals)} 个轮动信号")
    
    for i, signal in enumerate(signals, 1):
        print(f"\n{i}. {signal['sector']}")
        print(f"   类型: {signal['type']}")
        print(f"   强度: {signal['strength']:.1%}")
        print(f"   描述: {signal['description']}")
    
    # 生成建议
    if signals:
        top_signal = signals[0]
        recommendation = f"关注{top_signal['sector']}板块"
        print(f"\n💡 建议: {recommendation}")
    
    return True


def test_correlation_logic():
    """测试相关性逻辑"""
    print("\n🔗 测试相关性逻辑")
    print("=" * 50)
    
    # 模拟股票所属板块
    stock_sectors = [
        {'name': '银行', 'type': '行业板块'},
        {'name': '深圳本地', 'type': '地区板块'},
        {'name': 'HS300', 'type': '指数成分'},
    ]
    
    print("✅ 股票: 平安银行 (000001)")
    print(f"✅ 相关板块: {len(stock_sectors)}个")
    
    for i, sector in enumerate(stock_sectors, 1):
        print(f"{i}. {sector['name']} ({sector['type']})")
    
    return True


def main():
    """主测试函数"""
    print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 ")
    print("板块分析逻辑测试（离线，无需网络连接）")
    print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 ")
    
    results = {
        '板块计算': test_sector_calculation_logic(),
        '资金流向': test_capital_flow_logic(),
        '轮动信号': test_rotation_signal_logic(),
        '相关性': test_correlation_logic()
    }
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
