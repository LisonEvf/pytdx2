#!/usr/bin/env python3
# coding=utf-8
"""
机器学习策略测试脚本
测试：
1. 特征工程
2. LSTM策略
3. Random Forest策略
4. XGBoost策略
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_test_data(days: int = 500) -> pd.DataFrame:
    """创建测试数据（模拟2年日线数据）"""
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
        # 添加趋势和周期
        trend = 0.001 * np.sin(i / 30)
        cycle = 0.002 * np.cos(i / 60)
        
        # 生成价格
        change = np.random.randn() * 0.02 + trend + cycle
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


def test_feature_engineer():
    """测试特征工程"""
    print("\n" + "="*50)
    print("📊 测试特征工程")
    print("="*50)
    
    from tdx_mcp.backtest.ml_strategies import FeatureEngineer
    
    # 创建测试数据
    data = create_test_data(500)
    
    # 创建特征
    df_features = FeatureEngineer.create_features(data)
    
    print(f"✅ 原始数据列数: {len(data.columns)}")
    print(f"✅ 特征数据列数: {len(df_features.columns)}")
    
    # 检查特征
    feature_names = [
        'return_1d', 'return_5d', 'return_10d',
        'volatility_5d', 'volatility_10d', 'volatility_20d',
        'ma_5', 'ma_10', 'ma_20', 'ma_60',
        'bias_5', 'bias_10', 'bias_20',
        'rsi_14', 'macd', 'macd_signal', 'macd_hist',
        'boll_upper', 'boll_middle', 'boll_lower', 'boll_pct',
        'volume_ratio'
    ]
    
    print(f"\n📈 生成的特征（{len(feature_names)}个）:")
    for i, name in enumerate(feature_names[:10], 1):
        if name in df_features.columns:
            print(f"   {i}. {name}")
    
    # 准备ML数据
    X_train, X_test, y_train, y_test = FeatureEngineer.prepare_ml_data(df_features)
    
    print(f"\n✅ ML数据准备完成:")
    print(f"   训练集: {X_train.shape[0]} 样本")
    print(f"   测试集: {X_test.shape[0]} 样本")
    print(f"   特征数: {X_train.shape[1]}")
    
    return True


def test_random_forest_strategy():
    """测试随机森林策略"""
    print("\n" + "="*50)
    print("📊 测试随机森林策略")
    print("="*50)
    
    try:
        from tdx_mcp.backtest.ml_strategies import RandomForestStrategy
    except ImportError as e:
        print(f"⚠️  跳过测试: {e}")
        return True
    
    # 创建测试数据
    data = create_test_data(500)
    
    # 创建策略
    strategy = RandomForestStrategy({
        'n_estimators': 50,
        'max_depth': 5,
        'random_state': 42
    })
    
    print(f"✅ 策略: {strategy.get_name()}")
    
    # 训练模型
    print(f"\n🔧 训练模型...")
    train_result = strategy.train(data)
    
    print(f"✅ 训练完成:")
    print(f"   准确率: {train_result['accuracy']*100:.2f}%")
    print(f"   精确率: {train_result['precision']*100:.2f}%")
    print(f"   召回率: {train_result['recall']*100:.2f}%")
    
    # 显示特征重要性
    print(f"\n🎯 Top 5 重要特征:")
    importance = sorted(
        train_result['feature_importance'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    for i, (name, score) in enumerate(importance, 1):
        print(f"   {i}. {name}: {score:.4f}")
    
    # 生成信号
    signals = strategy.generate_signals(data)
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    
    print(f"\n✅ 信号生成:")
    print(f"   买入信号: {buy_signals} 次")
    print(f"   卖出信号: {sell_signals} 次")
    
    return True


def test_xgboost_strategy():
    """测试XGBoost策略"""
    print("\n" + "="*50)
    print("📊 测试XGBoost策略")
    print("="*50)
    
    try:
        from tdx_mcp.backtest.ml_strategies import XGBoostStrategy
    except ImportError as e:
        print(f"⚠️  跳过测试: {e}")
        return True
    
    # 创建测试数据
    data = create_test_data(500)
    
    # 创建策略
    strategy = XGBoostStrategy({
        'n_estimators': 50,
        'max_depth': 5,
        'learning_rate': 0.1
    })
    
    print(f"✅ 策略: {strategy.get_name()}")
    
    # 训练模型
    print(f"\n🔧 训练模型...")
    train_result = strategy.train(data)
    
    print(f"✅ 训练完成:")
    print(f"   MSE: {train_result['mse']:.6f}")
    print(f"   MAE: {train_result['mae']:.6f}")
    print(f"   方向准确率: {train_result['direction_accuracy']*100:.2f}%")
    
    # 生成信号
    signals = strategy.generate_signals(data)
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    
    print(f"\n✅ 信号生成:")
    print(f"   买入信号: {buy_signals} 次")
    print(f"   卖出信号: {sell_signals} 次")
    
    return True


def test_lstm_strategy():
    """测试LSTM策略（可选，需要TensorFlow）"""
    print("\n" + "="*50)
    print("📊 测试LSTM策略")
    print("="*50)
    
    try:
        from tdx_mcp.backtest.ml_strategies import LSTMStrategy
    except ImportError as e:
        print(f"⚠️  跳过测试: {e}")
        print(f"   提示: 安装TensorFlow以使用LSTM策略")
        return True
    
    # 创建测试数据
    data = create_test_data(300)  # LSTM需要较少数据
    
    # 创建策略
    strategy = LSTMStrategy({
        'look_back': 10,
        'epochs': 10,
        'batch_size': 16,
        'units': 32
    })
    
    print(f"✅ 策略: {strategy.get_name()}")
    
    # 训练模型
    print(f"\n🔧 训练模型（可能需要几分钟）...")
    train_result = strategy.train(data)
    
    print(f"✅ 训练完成:")
    print(f"   训练损失: {train_result['train_loss']:.4f}")
    print(f"   训练准确率: {train_result['train_accuracy']*100:.2f}%")
    print(f"   验证准确率: {train_result['val_accuracy']*100:.2f}%")
    print(f"   测试准确率: {train_result['test_accuracy']*100:.2f}%")
    
    # 生成信号
    signals = strategy.generate_signals(data)
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    
    print(f"\n✅ 信号生成:")
    print(f"   买入信号: {buy_signals} 次")
    print(f"   卖出信号: {sell_signals} 次")
    
    return True


def test_backtest_with_ml():
    """测试带ML策略的回测"""
    print("\n" + "="*50)
    print("📊 测试ML策略回测")
    print("="*50)
    
    try:
        from tdx_mcp.backtest.engine import BacktestEngine
        from tdx_mcp.backtest.ml_strategies import RandomForestStrategy
    except ImportError as e:
        print(f"⚠️  跳过测试: {e}")
        return True
    
    # 创建测试数据
    data = create_test_data(500)
    
    # 创建策略
    strategy = RandomForestStrategy({
        'n_estimators': 50,
        'max_depth': 5
    })
    
    # 创建回测引擎
    engine = BacktestEngine(initial_capital=1000000)
    
    # 运行回测
    print(f"✅ 策略: {strategy.get_name()}")
    print(f"\n🔧 运行回测...")
    
    result = engine.run_backtest(data, strategy, 'TEST_ML')
    
    print(f"\n📈 回测结果:")
    print(f"   初始资金: {result['initial_capital']:,.2f}元")
    print(f"   最终资金: {result['final_capital']:,.2f}元")
    print(f"   总收益率: {result['total_return']*100:.2f}%")
    print(f"   年化收益率: {result['annual_return']*100:.2f}%")
    print(f"   夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"   最大回撤: {result['max_drawdown']*100:.2f}%")
    print(f"   胜率: {result['win_rate']*100:.1f}%")
    print(f"   交易次数: {result['total_trades']} 次")
    
    return True


def test_ml_strategy_comparison():
    """ML策略对比"""
    print("\n" + "="*50)
    print("📊 ML策略对比测试")
    print("="*50)
    
    from tdx_mcp.backtest.engine import BacktestEngine
    from tdx_mcp.backtest.strategy_base import SMAStrategy, RSIStrategy, MACDStrategy
    
    strategies = [
        ('双均线', SMAStrategy({'fast_window': 10, 'slow_window': 20})),
        ('RSI', RSIStrategy()),
        ('MACD', MACDStrategy())
    ]
    
    # 尝试添加ML策略
    try:
        from tdx_mcp.backtest.ml_strategies import RandomForestStrategy
        strategies.append(('RandomForest', RandomForestStrategy({'n_estimators': 50})))
    except:
        pass
    
    try:
        from tdx_mcp.backtest.ml_strategies import XGBoostStrategy
        strategies.append(('XGBoost', XGBoostStrategy({'n_estimators': 50})))
    except:
        pass
    
    # 创建测试数据
    data = create_test_data(500)
    
    # 运行回测
    results = []
    for name, strategy in strategies:
        try:
            engine = BacktestEngine(initial_capital=1000000)
            result = engine.run_backtest(data, strategy, 'TEST')
            results.append({
                'strategy': name,
                'total_return': result['total_return'],
                'sharpe_ratio': result['sharpe_ratio'],
                'max_drawdown': result['max_drawdown'],
                'win_rate': result['win_rate']
            })
        except Exception as e:
            print(f"⚠️  {name} 策略失败: {e}")
    
    # 排序
    results.sort(key=lambda x: x['total_return'], reverse=True)
    
    print(f"\n📈 策略对比（按收益率排序）:")
    print("-" * 70)
    print(f"{'策略名称':<15} {'收益率':>8} {'夏普比率':>8} {'最大回撤':>8} {'胜率':>8}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['strategy']:<15} {r['total_return']*100:>7.2f}% {r['sharpe_ratio']:>8.2f} "
              f"{r['max_drawdown']*100:>7.2f}% {r['win_rate']*100:>7.1f}%")
    
    print("-" * 70)
    
    return True


def main():
    """主测试函数"""
    print("\n")
    print("🚀 " * 20)
    print("机器学习策略测试")
    print("🚀 " * 20)
    
    tests = [
        ("特征工程", test_feature_engineer),
        ("随机森林策略", test_random_forest_strategy),
        ("XGBoost策略", test_xgboost_strategy),
        ("LSTM策略", test_lstm_strategy),
        ("ML策略回测", test_backtest_with_ml),
        ("策略对比", test_ml_strategy_comparison)
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
            import traceback
            traceback.print_exc()
    
    # 打印总结
    print("\n" + "="*50)
    print("📋 测试总结")
    print("="*50)
    
    for name, success, error in results:
        if success:
            print(f"✅ {name}")
        else:
            print(f"⚠️  {name}: {error if error else '跳过'}")
    
    # 统计
    success_count = sum(1 for _, success, _ in results if success)
    print(f"\n总计: {success_count}/{len(results)} 通过")
    
    if success_count == len(results):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试跳过或失败")
        return 1


if __name__ == '__main__':
    exit(main())
