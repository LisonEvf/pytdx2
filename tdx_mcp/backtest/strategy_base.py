# coding=utf-8
"""
策略基类模块
功能：
1. 定义策略接口
2. 提供常用指标计算
3. 信号生成框架
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """
    策略基类
    
    所有策略必须实现：
    - generate_signals(): 生成买卖信号
    - get_name(): 策略名称
    - get_params(): 策略参数
    
    可选实现：
    - calculate_indicators(): 计算指标
    - validate_params(): 验证参数
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化策略
        
        Args:
            params: 策略参数字典
        """
        self.params = params or {}
        self.indicators = {}
        
        # 验证参数
        if not self.validate_params():
            raise ValueError(f"Invalid strategy parameters: {self.params}")
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成买卖信号
        
        Args:
            data: 股票数据（包含OHLCV等）
        
        Returns:
            DataFrame，包含signal列：
            - 1: 买入
            - -1: 卖出
            - 0: 持有/空仓
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取策略名称"""
        pass
    
    def get_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return self.params
    
    def validate_params(self) -> bool:
        """验证参数（子类可重写）"""
        return True
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算指标（子类可重写）
        
        Args:
            data: 股票数据
        
        Returns:
            指标字典
        """
        return {}
    
    # ==================== 常用指标计算方法 ====================
    
    @staticmethod
    def sma(series: pd.Series, window: int) -> pd.Series:
        """简单移动平均"""
        return series.rolling(window=window, min_periods=window).mean()
    
    @staticmethod
    def ema(series: pd.Series, window: int) -> pd.Series:
        """指数移动平均"""
        return series.ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def rsi(close: pd.Series, window: int = 14) -> pd.Series:
        """相对强弱指标"""
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD指标"""
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(close: pd.Series, window: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """布林带"""
        middle = close.rolling(window=window).mean()
        std = close.rolling(window=window).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """真实波动幅度"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        
        return atr
    
    @staticmethod
    def cross_above(series1: pd.Series, series2: pd.Series) -> pd.Series:
        """上穿信号"""
        return (series1 > series2) & (series1.shift(1) <= series2.shift(1))
    
    @staticmethod
    def cross_below(series1: pd.Series, series2: pd.Series) -> pd.Series:
        """下穿信号"""
        return (series1 < series2) & (series1.shift(1) >= series2.shift(1))


class SMAStrategy(BaseStrategy):
    """
    双均线策略示例
    
    参数：
    - fast_window: 快线周期（默认10）
    - slow_window: 慢线周期（默认20）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'fast_window': 10,
            'slow_window': 20
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_name(self) -> str:
        return "双均线策略"
    
    def validate_params(self) -> bool:
        fast = self.params.get('fast_window', 10)
        slow = self.params.get('slow_window', 20)
        
        # 快线必须小于慢线
        return fast > 0 and slow > 0 and fast < slow
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成信号
        
        买入信号：快线上穿慢线
        卖出信号：快线下穿慢线
        """
        df = data.copy()
        
        # 计算均线
        fast_window = self.params['fast_window']
        slow_window = self.params['slow_window']
        
        df['fast_ma'] = self.sma(df['close'], fast_window)
        df['slow_ma'] = self.sma(df['close'], slow_window)
        
        # 生成信号
        df['signal'] = 0
        
        # 上穿买入
        df.loc[self.cross_above(df['fast_ma'], df['slow_ma']), 'signal'] = 1
        
        # 下穿卖出
        df.loc[self.cross_below(df['fast_ma'], df['slow_ma']), 'signal'] = -1
        
        return df


class RSIStrategy(BaseStrategy):
    """
    RSI策略示例
    
    参数：
    - rsi_window: RSI周期（默认14）
    - oversold: 超卖阈值（默认30）
    - overbought: 超买阈值（默认70）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'rsi_window': 14,
            'oversold': 30,
            'overbought': 70
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_name(self) -> str:
        return "RSI策略"
    
    def validate_params(self) -> bool:
        oversold = self.params.get('oversold', 30)
        overbought = self.params.get('overbought', 70)
        
        # 超卖必须小于超买
        return 0 <= oversold < overbought <= 100
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成信号
        
        买入信号：RSI从超卖区回升
        卖出信号：RSI从超买区回落
        """
        df = data.copy()
        
        rsi_window = self.params['rsi_window']
        oversold = self.params['oversold']
        overbought = self.params['overbought']
        
        # 计算RSI
        df['rsi'] = self.rsi(df['close'], rsi_window)
        
        # 生成信号
        df['signal'] = 0
        
        # RSI从超卖区回升
        df.loc[(df['rsi'].shift(1) < oversold) & (df['rsi'] >= oversold), 'signal'] = 1
        
        # RSI从超买区回落
        df.loc[(df['rsi'].shift(1) > overbought) & (df['rsi'] <= overbought), 'signal'] = -1
        
        return df


class MACDStrategy(BaseStrategy):
    """
    MACD策略示例
    
    参数：
    - fast: 快线周期（默认12）
    - slow: 慢线周期（默认26）
    - signal: 信号线周期（默认9）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'fast': 12,
            'slow': 26,
            'signal': 9
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_name(self) -> str:
        return "MACD策略"
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成信号
        
        买入信号：MACD上穿信号线
        卖出信号：MACD下穿信号线
        """
        df = data.copy()
        
        fast = self.params['fast']
        slow = self.params['slow']
        signal_period = self.params['signal']
        
        # 计算MACD
        macd_line, signal_line, histogram = self.macd(df['close'], fast, slow, signal_period)
        
        df['macd'] = macd_line
        df['signal_line'] = signal_line
        df['histogram'] = histogram
        
        # 生成信号
        df['signal'] = 0
        
        # 上穿买入
        df.loc[self.cross_above(df['macd'], df['signal_line']), 'signal'] = 1
        
        # 下穿卖出
        df.loc[self.cross_below(df['macd'], df['signal_line']), 'signal'] = -1
        
        return df


# 导出策略类
__all__ = [
    'BaseStrategy',
    'SMAStrategy',
    'RSIStrategy',
    'MACDStrategy'
]
