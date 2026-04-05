# coding=utf-8
"""
回测框架测试脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/lisonevf/Documents/pytdx2')

from tdx_mcp.backtest.strategy_base import SMAStrategy, RSIStrategy, MACDStrategy
from tdx_mcp.backtest.engine import BacktestEngine
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_mock_data(days: int = 100) -> pd.DataFrame:
    """
    生成模拟股票数据
    
    Args:
        days: 天数
    
    Returns:
        DataFrame，包含OHLCV数据
    """
    np.random.seed(42)
    
    # 生成日期
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    
    # 生成价格数据
    initial_price = 10.0
    returns = np.random.normal(0.001, 0.02, days)  # 日收益率
    prices = initial_price * np.cumprod(1 + returns)
    
    # 生成OHLCV数据
    data = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'high': prices * (1 + np.random.uniform(0, 0.02, days)),
        'low': prices * (1 - np.random.uniform(0, 0.02, days)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, days)
    })
    
    # 确保价格逻辑正确
    data['high'] = data[['open', 'close', 'high']].max(axis=1)
    data['low'] = data[['open', 'close', 'low']].min(axis=1)
    
    return data


def test_sma_strategy():
    """测试双均线策略"""
    print("\n📊 测试双均线策略")
    print("=" * 50)
    
    # 生成数据
    data = generate_mock_data(200)
    
    # 创建策略
    strategy = SMAStrategy({
        'fast_window': 10,
        'slow_window': 20
    })
    
    print(f"✅ 策略: {strategy.get_name()}")
    print(f"✅ 参数: {strategy.get_params()}")
    
    # 创建回测引擎
    engine = BacktestEngine(
        initial_capital=1000000,
        commission_rate=0.0003,
        slippage_rate=0.0001
    )
    
    # 执行回测
    result = engine.run_backtest(data, strategy, stock_code='MOCK001')
    
    # 打印结果
    print(f"\n📈 回测结果:")
    print(f"初始资金: {result['initial_capital']:,.2f}元")
    print(f"最终资金: {result['final_capital']:,.2f}元")
    print(f"总收益率: {result['total_return']*100:.2f}%")
    print(f"年化收益率: {result['annual_return']*100:.2f}%")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"最大回撤: {result['max_drawdown']*100:.2f}%")
    print(f"胜率: {result['win_rate']*100:.2f}%")
    print(f"交易次数: {result['total_trades']}")
    
    return True


def test_rsi_strategy():
    """测试RSI策略"""
    print("\n📊 测试RSI策略")
    print("=" * 50)
    
    # 生成数据
    data = generate_mock_data(200)
    
    # 创建策略
    strategy = RSIStrategy({
        'rsi_window': 14,
        'oversold': 30,
        'overbought': 70
    })
    
    print(f"✅ 策略: {strategy.get_name()}")
    print(f"✅ 参数: {strategy.get_params()}")
    
    # 创建回测引擎
    engine = BacktestEngine(initial_capital=1000000)
    
    # 执行回测
    result = engine.run_backtest(data, strategy, stock_code='MOCK001')
    
    # 打印结果
    print(f"\n📈 回测结果:")
    print(f"总收益率: {result['total_return']*100:.2f}%")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"最大回撤: {result['max_drawdown']*100:.2f}%")
    print(f"交易次数: {result['total_trades']}")
    
    return True


def test_macd_strategy():
    """测试MACD策略"""
    print("\n📊 测试MACD策略")
    print("=" * 50)
    
    # 生成数据
    data = generate_mock_data(200)
    
    # 创建策略
    strategy = MACDStrategy({
        'fast': 12,
        'slow': 26,
        'signal': 9
    })
    
    print(f"✅ 策略: {strategy.get_name()}")
    print(f"✅ 参数: {strategy.get_params()}")
    
    # 创建回测引擎
    engine = BacktestEngine(initial_capital=1000000)
    
    # 执行回测
    result = engine.run_backtest(data, strategy, stock_code='MOCK001')
    
    # 打印结果
    print(f"\n📈 回测结果:")
    print(f"总收益率: {result['total_return']*100:.2f}%")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"最大回撤: {result['max_drawdown']*100:.2f}%")
    print(f"交易次数: {result['total_trades']}")
    
    return True


def test_strategy_comparison():
    """测试策略对比"""
    print("\n📊 测试策略对比")
    print("=" * 50)
    
    # 生成数据
    data = generate_mock_data(300)
    
    # 创建多个策略
    strategies = [
        SMAStrategy({'fast_window': 5, 'slow_window': 20}),
        RSIStrategy({'rsi_window': 14, 'oversold': 30, 'overbought': 70}),
        MACDStrategy({'fast': 12, 'slow': 26, 'signal': 9})
    ]
    
    results = []
    
    for strategy in strategies:
        engine = BacktestEngine(initial_capital=1000000)
        result = engine.run_backtest(data, strategy, stock_code='MOCK001')
        
        results.append({
            'strategy': strategy.get_name(),
            'return': result['total_return'],
            'sharpe': result['sharpe_ratio'],
            'drawdown': result['max_drawdown'],
            'trades': result['total_trades']
        })
    
    # 打印对比结果
    print("\n📈 策略对比:")
    print("-" * 70)
    print(f"{'策略':<15} {'收益率':<12} {'夏普':<10} {'最大回撤':<12} {'交易次数':<10}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['strategy']:<15} {r['return']*100:>10.2f}% {r['sharpe']:>8.2f} "
              f"{r['drawdown']*100:>10.2f}% {r['trades']:>8}")
    
    print("-" * 70)
    
    return True


def main():
    """主测试函数"""
    print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 ")
    print("回测框架测试（离线，使用模拟数据）")
    print("🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 🚀 ")
    
    results = {
        '双均线策略': test_sma_strategy(),
        'RSI策略': test_rsi_strategy(),
        'MACD策略': test_macd_strategy(),
        '策略对比': test_strategy_comparison()
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
