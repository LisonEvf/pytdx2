#!/usr/bin/env python3
# coding=utf-8
"""
高级回测功能测试脚本
测试：
1. 风险管理模块
2. 高级策略（布林带、KDJ、量价、多因子、海龟）
3. 完整回测流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_test_data(days: int = 250) -> pd.DataFrame:
    """创建测试数据（模拟1年日线数据）"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 模拟价格数据（带趋势的随机游走）
    np.random.seed(42)
    
    close = 100  # 初始价格
    closes = []
    highs = []
    lows = []
    opens = []
    volumes = []
    
    for i in range(days):
        # 添加趋势
        trend = 0.001 * np.sin(i / 30)  # 周期性趋势
        
        # 生成价格
        change = np.random.randn() * 0.02 + trend
        close = close * (1 + change)
        
        # 生成OHLC
        open_price = close * (1 + np.random.randn() * 0.005)
        high = max(open_price, close) * (1 + abs(np.random.randn() * 0.01))
        low = min(open_price, close) * (1 - abs(np.random.randn() * 0.01))
        volume = 1000000 * (1 + np.random.randn() * 0.3)
        
        closes.append(close)
        opens.append(open_price)
        highs.append(high)
        lows.append(low)
        volumes.append(volume)
    
    df = pd.DataFrame({
        'date': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })
    
    return df


def test_risk_manager():
    """测试风险管理模块"""
    print("\n" + "="*50)
    print("📊 测试风险管理模块")
    print("="*50)
    
    from tdx_mcp.backtest.risk_manager import RiskManager, PortfolioRiskManager
    
    # 创建风险管理器
    risk_mgr = RiskManager(params={
        'stop_loss_pct': 0.05,
        'take_profit_pct': 0.15,
        'trailing_stop_pct': 0.03,
        'trailing_stop_trigger': 0.05,
        'max_holding_days': 20,
        'position_sizing': 'volatility'
    })
    
    print(f"✅ 风险管理器创建成功")
    
    # 模拟买入
    entry_price = 100.0
    entry_date = datetime.now() - timedelta(days=10)
    atr = 3.0
    
    risk_params = risk_mgr.on_buy(entry_price, entry_date, atr)
    print(f"✅ 买入风控参数:")
    print(f"   入场价: {risk_params['entry_price']:.2f}")
    print(f"   止损价: {risk_params['stop_loss_price']:.2f}")
    print(f"   止盈价: {risk_params['take_profit_price']:.2f}")
    print(f"   ATR止损: {risk_params['atr_stop_price']:.2f}")
    
    # 测试止损触发
    current_price = 94.0  # 下跌6%
    should_sell, reason = risk_mgr.check_sell_signal(
        current_price, datetime.now(), 1000000
    )
    print(f"\n✅ 价格跌至 {current_price}（-6%）:")
    print(f"   应该卖出: {should_sell}")
    print(f"   原因: {reason}")
    
    # 测试移动止损
    risk_mgr.on_buy(entry_price, datetime.now() - timedelta(days=5), atr)
    current_price = 107.0  # 盈利7%
    should_sell, reason = risk_mgr.check_sell_signal(
        current_price, datetime.now(), 1050000
    )
    print(f"\n✅ 价格涨至 {current_price}（+7%）:")
    print(f"   应该卖出: {should_sell}")
    print(f"   原因: {reason}")
    
    # 测试仓位计算
    capital = 1000000
    position_size = risk_mgr.calculate_position_size(capital, entry_price, atr=atr)
    print(f"\n✅ 仓位计算:")
    print(f"   可用资金: {capital:,.0f}")
    print(f"   建议买入: {position_size} 股")
    print(f"   买入金额: {position_size * entry_price:,.0f}")
    
    # 测试组合风险管理
    portfolio_mgr = PortfolioRiskManager(params={
        'max_positions': 5,
        'max_single_position_pct': 0.2
    })
    
    print(f"\n✅ 组合风险管理器创建成功")
    
    # 检查是否可以买入
    can_buy, reason = portfolio_mgr.can_add_position('000001.SZ', '银行')
    print(f"   可以买入000001.SZ: {can_buy} ({reason})")
    
    return True


def test_advanced_strategies():
    """测试高级策略"""
    print("\n" + "="*50)
    print("📊 测试高级策略")
    print("="*50)
    
    from tdx_mcp.backtest.advanced_strategies import (
        BollingerBandsStrategy,
        KDJStrategy,
        VolumePriceStrategy,
        MultiFactorStrategy,
        TurtleStrategy
    )
    
    # 创建测试数据
    data = create_test_data(250)
    print(f"✅ 创建测试数据: {len(data)} 天")
    
    # 测试布林带策略
    print("\n--- 布林带策略（突破模式）---")
    bb_strategy = BollingerBandsStrategy({'mode': 'breakout'})
    signals = bb_strategy.generate_signals(data)
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    print(f"✅ 策略: {bb_strategy.get_name()}")
    print(f"   买入信号: {buy_signals} 次")
    print(f"   卖出信号: {sell_signals} 次")
    
    # 测试KDJ策略
    print("\n--- KDJ策略 ---")
    kdj_strategy = KDJStrategy({'oversold': 20, 'overbought': 80})
    signals = kdj_strategy.generate_signals(data)
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    print(f"✅ 策略: {kdj_strategy.get_name()}")
    print(f"   买入信号: {buy_signals} 次")
    print(f"   卖出信号: {sell_signals} 次")
    
    # 测试量价策略
    print("\n--- 量价策略 ---")
    vp_strategy = VolumePriceStrategy()
    signals = vp_strategy.generate_signals(data)
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    print(f"✅ 策略: {vp_strategy.get_name()}")
    print(f"   买入信号: {buy_signals} 次")
    print(f"   卖出信号: {sell_signals} 次")
    
    # 测试多因子策略
    print("\n--- 多因子策略 ---")
    mf_strategy = MultiFactorStrategy({
        'factors': ['rsi', 'macd', 'volume', 'momentum'],
        'buy_threshold': 0.5,
        'sell_threshold': -0.5
    })
    signals = mf_strategy.generate_signals(data)
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    print(f"✅ 策略: {mf_strategy.get_name()}")
    print(f"   买入信号: {buy_signals} 次")
    print(f"   卖出信号: {sell_signals} 次")
    
    # 测试海龟策略
    print("\n--- 海龟策略 ---")
    turtle_strategy = TurtleStrategy({
        'entry_window': 20,
        'exit_window': 10
    })
    signals = turtle_strategy.generate_signals(data)
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    print(f"✅ 策略: {turtle_strategy.get_name()}")
    print(f"   买入信号: {buy_signals} 次")
    print(f"   卖出信号: {sell_signals} 次")
    
    return True


def test_backtest_with_risk_management():
    """测试带风险管理的回测"""
    print("\n" + "="*50)
    print("📊 测试带风险管理的回测")
    print("="*50)
    
    from tdx_mcp.backtest.engine import BacktestEngine
    from tdx_mcp.backtest.strategy_base import SMAStrategy
    from tdx_mcp.backtest.risk_manager import RiskManager
    
    # 创建测试数据
    data = create_test_data(250)
    
    # 创建策略
    strategy = SMAStrategy({'fast_window': 10, 'slow_window': 20})
    
    # 创建回测引擎
    engine = BacktestEngine(
        initial_capital=1000000,
        commission_rate=0.0003,
        slippage_rate=0.0001,
        position_size=0.95
    )
    
    # 运行回测
    result = engine.run_backtest(data, strategy, 'TEST')
    
    print(f"✅ 策略: {result['strategy_name']}")
    print(f"\n📈 回测结果:")
    print(f"   初始资金: {result['initial_capital']:,.2f}元")
    print(f"   最终资金: {result['final_capital']:,.2f}元")
    print(f"   总收益率: {result['total_return']*100:.2f}%")
    print(f"   年化收益率: {result['annual_return']*100:.2f}%")
    print(f"   夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"   最大回撤: {result['max_drawdown']*100:.2f}%")
    print(f"   胜率: {result['win_rate']*100:.1f}%")
    print(f"   交易次数: {result['total_trades']} 次")
    
    # 测试风险管理的应用
    print(f"\n🔍 风险管理测试:")
    risk_mgr = RiskManager({'stop_loss_pct': 0.05, 'take_profit_pct': 0.10})
    
    # 模拟应用止损止盈
    trades_with_risk = []
    for trade in result['trades']:
        if trade['type'] == 'BUY':
            risk_mgr.on_buy(trade['price'], trade['date'])
            trades_with_risk.append(trade)
        elif trade['type'] == 'SELL':
            # 检查是否触发风控
            should_sell, reason = risk_mgr.check_sell_signal(
                trade['price'], trade['date']
            )
            trade['risk_check'] = should_sell
            trade['risk_reason'] = reason if should_sell else '正常卖出'
            trades_with_risk.append(trade)
    
    print(f"✅ 交易记录已添加风控检查")
    
    return True


def test_strategy_comparison():
    """策略对比测试"""
    print("\n" + "="*50)
    print("📊 策略对比测试")
    print("="*50)
    
    from tdx_mcp.backtest.engine import BacktestEngine
    from tdx_mcp.backtest.strategy_base import SMAStrategy, RSIStrategy, MACDStrategy
    from tdx_mcp.backtest.advanced_strategies import (
        BollingerBandsStrategy,
        KDJStrategy,
        TurtleStrategy
    )
    
    # 创建测试数据（2年）
    data = create_test_data(500)
    
    # 创建策略列表
    strategies = [
        SMAStrategy({'fast_window': 10, 'slow_window': 20}),
        RSIStrategy({'rsi_window': 14, 'oversold': 30, 'overbought': 70}),
        MACDStrategy(),
        BollingerBandsStrategy({'mode': 'reversal'}),
        KDJStrategy(),
        TurtleStrategy()
    ]
    
    # 运行回测
    results = []
    for strategy in strategies:
        engine = BacktestEngine(initial_capital=1000000)
        result = engine.run_backtest(data, strategy, 'TEST')
        results.append({
            'strategy': strategy.get_name(),
            'total_return': result['total_return'],
            'sharpe_ratio': result['sharpe_ratio'],
            'max_drawdown': result['max_drawdown'],
            'win_rate': result['win_rate'],
            'trades': result['total_trades']
        })
    
    # 排序（按收益率）
    results.sort(key=lambda x: x['total_return'], reverse=True)
    
    print(f"\n📈 策略对比（按收益率排序）:")
    print("-" * 80)
    print(f"{'策略名称':<15} {'收益率':>8} {'夏普比率':>8} {'最大回撤':>8} {'胜率':>8} {'交易次数':>8}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['strategy']:<15} {r['total_return']*100:>7.2f}% {r['sharpe_ratio']:>8.2f} "
              f"{r['max_drawdown']*100:>7.2f}% {r['win_rate']*100:>7.1f}% {r['trades']:>8}")
    
    print("-" * 80)
    
    # 找出最佳策略
    best = results[0]
    print(f"\n✅ 最佳策略: {best['strategy']}")
    print(f"   收益率: {best['total_return']*100:.2f}%")
    print(f"   夏普比率: {best['sharpe_ratio']:.2f}")
    
    return True


def main():
    """主测试函数"""
    print("\n")
    print("🚀 " * 20)
    print("高级回测功能测试")
    print("🚀 " * 20)
    
    tests = [
        ("风险管理模块", test_risk_manager),
        ("高级策略", test_advanced_strategies),
        ("带风险管理的回测", test_backtest_with_risk_management),
        ("策略对比", test_strategy_comparison)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            print(f"\n▶️  测试: {name}")
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"❌ 测试失败: {e}")
    
    # 打印总结
    print("\n" + "="*50)
    print("📋 测试总结")
    print("="*50)
    
    for name, success, error in results:
        if success:
            print(f"✅ {name}")
        else:
            print(f"❌ {name}: {error}")
    
    # 统计
    success_count = sum(1 for _, success, _ in results if success)
    print(f"\n总计: {success_count}/{len(results)} 通过")
    
    if success_count == len(results):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败")
        return 1


if __name__ == '__main__':
    exit(main())
