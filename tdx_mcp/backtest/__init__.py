# coding=utf-8
"""
pytdx2 Tick级回测框架

支持QMT代码兼容的tick级回测引擎
"""

from .engine import BacktestEngine
from .strategy import BaseStrategy
from .context import ContextInfo
from .portfolio import Portfolio
from .analyzer import PerformanceAnalyzer

__all__ = [
    'BacktestEngine',
    'BaseStrategy',
    'ContextInfo',
    'Portfolio',
    'PerformanceAnalyzer'
]

__version__ = '1.0.0'
