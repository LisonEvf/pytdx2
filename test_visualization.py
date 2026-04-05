# coding=utf-8
"""
可视化功能测试脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/lisonevf/Documents/pytdx2')

from tdx_mcp.backtest.visualization import ChartGenerator
from tdx_mcp.backtest.strategy_base import SMAStrategy
from tdx_mcp.backtest.engine import BacktestEngine
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_mock_data(days: int = 100) -> pd.DataFrame:
    """生成模拟股票数据"""
    np.random.seed(42)
    
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    
    initial_price = 10.0
    returns = np.random.normal(0.001, 0.02, days)
    prices = initial_price * np.cumprod(1 + returns)
    
    data = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'high': prices * (1 + np.random.uniform(0, 0.02, days)),
        'low': prices * (1 - np.random.uniform(0, 0.02, days)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, days)
    })
    
    data['high'] = data[['open', 'close', 'high']].max(axis=1)
    data['low'] = data[['open', 'close', 'low']].min(axis=1)
    
    return data


def test_candlestick_chart():
    """测试K线图生成"""
    print("\n📊 测试K线图生成")
    print("=" * 50)
    
    # 生成数据
    data = generate_mock_data(100)
    
    # 创建图表生成器
    chart = ChartGenerator()
    
    # 生成K线图（保存到文件）
    output_path = '/tmp/candlestick_test.png'
    chart.plot_candlestick(
        data,
        title='测试股票K线图',
        ma_periods=[5, 10, 20],
        volume=True,
        save_path=output_path
    )
    
    # 检查文件是否存在
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✅ K线图生成成功")
        print(f"   文件路径: {output_path}")
        print(f"   文件大小: {file_size/1024:.2f} KB")
        return True
    else:
        print("❌ K线图生成失败")
        return False


def test_indicator_chart():
    """测试技术指标图"""
    print("\n📊 测试技术指标图")
    print("=" * 50)
    
    # 生成数据
    data = generate_mock_data(100)
    
    # 计算指标
    indicators = {
        'RSI': (data['close'].diff().apply(lambda x: max(x, 0)).rolling(14).mean() / 
                data['close'].diff().apply(lambda x: abs(x)).rolling(14).mean() * 100),
        'MACD': data['close'].ewm(span=12).mean() - data['close'].ewm(span=26).mean()
    }
    
    # 创建图表生成器
    chart = ChartGenerator()
    
    # 生成带指标的图表
    output_path = '/tmp/indicator_test.png'
    chart.plot_with_indicators(
        data,
        indicators,
        title='技术指标图',
        save_path=output_path
    )
    
    # 检查文件
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✅ 技术指标图生成成功")
        print(f"   文件路径: {output_path}")
        print(f"   文件大小: {file_size/1024:.2f} KB")
        return True
    else:
        print("❌ 技术指标图生成失败")
        return False


def test_backtest_visualization():
    """测试回测结果可视化"""
    print("\n📊 测试回测结果可视化")
    print("=" * 50)
    
    # 生成数据
    data = generate_mock_data(200)
    
    # 执行回测
    strategy = SMAStrategy({'fast_window': 10, 'slow_window': 20})
    engine = BacktestEngine(initial_capital=1000000)
    result = engine.run_backtest(data, strategy, stock_code='TEST')
    
    # 创建图表生成器
    chart = ChartGenerator()
    
    # 生成回测结果图
    output_path = '/tmp/backtest_test.png'
    chart.plot_backtest_result(
        result['daily_values'],
        result['trades'],
        title=f'回测结果 - {strategy.get_name()}',
        save_path=output_path
    )
    
    # 检查文件
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✅ 回测结果图生成成功")
        print(f"   文件路径: {output_path}")
        print(f"   文件大小: {file_size/1024:.2f} KB")
        print(f"\n   回测绩效:")
        print(f"   总收益率: {result['total_return']*100:.2f}%")
        print(f"   夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"   最大回撤: {result['max_drawdown']*100:.2f}%")
        return True
    else:
        print("❌ 回测结果图生成失败")
        return False


def test_strategy_comparison():
    """测试策略对比图"""
    print("\n📊 测试策略对比图")
    print("=" * 50)
    
    # 模拟策略结果
    results = [
        {'strategy': '双均线', 'return': 0.12, 'sharpe': 0.8, 'drawdown': 0.15},
        {'strategy': 'RSI', 'return': 0.25, 'sharpe': 1.2, 'drawdown': 0.10},
        {'strategy': 'MACD', 'return': 0.18, 'sharpe': 0.9, 'drawdown': 0.12}
    ]
    
    # 创建图表生成器
    chart = ChartGenerator()
    
    # 生成对比图
    output_path = '/tmp/comparison_test.png'
    chart.plot_strategy_comparison(
        results,
        title='策略性能对比',
        save_path=output_path
    )
    
    # 检查文件
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✅ 策略对比图生成成功")
        print(f"   文件路径: {output_path}")
        print(f"   文件大小: {file_size/1024:.2f} KB")
        return True
    else:
        print("❌ 策略对比图生成失败")
        return False


def main():
    """主测试函数"""
    print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 ")
    print("可视化功能测试")
    print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 ")
    
    results = {
        'K线图': test_candlestick_chart(),
        '技术指标图': test_indicator_chart(),
        '回测结果图': test_backtest_visualization(),
        '策略对比图': test_strategy_comparison()
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
    
    print("\n💡 提示:")
    print("- 图表已保存到 /tmp/ 目录")
    print("- 可以使用图片查看器打开")
    print("- 支持PNG高清格式（300 DPI）")
    
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
