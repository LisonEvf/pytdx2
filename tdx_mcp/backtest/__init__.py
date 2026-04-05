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

from .advanced_strategies import (
    BollingerBandsStrategy,
    KDJStrategy,
    VolumePriceStrategy,
    MultiFactorStrategy,
    TurtleStrategy
)

from .engine import (
    BacktestEngine,
    run_multi_stock_backtest
)

from .visualization import ChartGenerator

from .risk_manager import (
    RiskManager,
    PortfolioRiskManager
)

__all__ = [
    # 基础策略
    'BaseStrategy',
    'SMAStrategy',
    'RSIStrategy',
    'MACDStrategy',
    
    # 高级策略
    'BollingerBandsStrategy',
    'KDJStrategy',
    'VolumePriceStrategy',
    'MultiFactorStrategy',
    'TurtleStrategy',
    
    # 回测引擎
    'BacktestEngine',
    'run_multi_stock_backtest',
    
    # 可视化
    'ChartGenerator',
    
    # 风险管理
    'RiskManager',
    'PortfolioRiskManager'
]
