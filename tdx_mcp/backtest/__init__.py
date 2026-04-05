# coding=utf-8
"""
回测框架模块
"""
from .strategy_base import (
    BaseStrategy,
    SMAStrategy,
    RSIStrategy,
    MACDStrategy
)

from .engine import (
    BacktestEngine,
    run_multi_stock_backtest
)

__all__ = [
    # 策略基类
    'BaseStrategy',
    'SMAStrategy',
    'RSIStrategy',
    'MACDStrategy',
    
    # 回测引擎
    'BacktestEngine',
    'run_multi_stock_backtest'
]
