# coding=utf-8
"""
高级策略模块
功能：
1. 布林带策略
2. KDJ策略
3. 量价策略
4. 多因子组合策略
"""
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from .strategy_base import BaseStrategy


class BollingerBandsStrategy(BaseStrategy):
    """
    布林带策略
    
    参数：
    - window: 布林带周期（默认20）
    - std_dev: 标准差倍数（默认2）
    - mode: 策略模式（'breakout'突破/ 'reversal'回归）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'window': 20,
            'std_dev': 2,
            'mode': 'breakout'  # breakout/reversal
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_name(self) -> str:
        mode = self.params.get('mode', 'breakout')
        return f"布林带策略（{mode}）"
    
    def validate_params(self) -> bool:
        window = self.params.get('window', 20)
        std_dev = self.params.get('std_dev', 2)
        
        return window > 0 and std_dev > 0
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成信号
        
        突破模式：
        - 买入：价格突破上轨
        - 卖出：价格跌破下轨
        
        回归模式：
        - 买入：价格触及下轨
        - 卖出：价格触及上轨
        """
        df = data.copy()
        
        window = self.params['window']
        std_dev = self.params['std_dev']
        mode = self.params['mode']
        
        # 计算布林带
        df['middle'] = df['close'].rolling(window=window).mean()
        df['std'] = df['close'].rolling(window=window).std()
        df['upper'] = df['middle'] + (df['std'] * std_dev)
        df['lower'] = df['middle'] - (df['std'] * std_dev)
        df['bandwidth'] = (df['upper'] - df['lower']) / df['middle']
        
        # 生成信号
        df['signal'] = 0
        
        if mode == 'breakout':
            # 突破模式
            # 买入：价格突破上轨
            df.loc[df['close'] > df['upper'], 'signal'] = 1
            
            # 卖出：价格跌破下轨
            df.loc[df['close'] < df['lower'], 'signal'] = -1
        
        elif mode == 'reversal':
            # 回归模式
            # 买入：价格触及下轨（超卖）
            df.loc[df['close'] <= df['lower'], 'signal'] = 1
            
            # 卖出：价格触及上轨（超买）
            df.loc[df['close'] >= df['upper'], 'signal'] = -1
        
        return df


class KDJStrategy(BaseStrategy):
    """
    KDJ策略
    
    参数：
    - n: KDJ周期（默认9）
    - m1: K值平滑周期（默认3）
    - m2: D值平滑周期（默认3）
    - oversold: 超卖阈值（默认20）
    - overbought: 超买阈值（默认80）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'n': 9,
            'm1': 3,
            'm2': 3,
            'oversold': 20,
            'overbought': 80
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_name(self) -> str:
        return "KDJ策略"
    
    def validate_params(self) -> bool:
        oversold = self.params.get('oversold', 20)
        overbought = self.params.get('overbought', 80)
        
        return 0 <= oversold < overbought <= 100
    
    def _calculate_kdj(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        n: int = 9,
        m1: int = 3,
        m2: int = 3
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算KDJ指标
        
        Args:
            high: 最高价
            low: 最低价
            close: 收盘价
            n: 周期
            m1: K值平滑周期
            m2: D值平滑周期
        
        Returns:
            (K, D, J)
        """
        # 计算RSV
        low_n = low.rolling(window=n, min_periods=1).min()
        high_n = high.rolling(window=n, min_periods=1).max()
        
        rsv = (close - low_n) / (high_n - low_n) * 100
        
        # 计算K值（RSV的平滑）
        k = rsv.ewm(alpha=1/m1, adjust=False).mean()
        
        # 计算D值（K值的平滑）
        d = k.ewm(alpha=1/m2, adjust=False).mean()
        
        # 计算J值
        j = 3 * k - 2 * d
        
        return k, d, j
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成信号
        
        买入信号：
        - K线上穿D线
        - K、D值在超卖区
        
        卖出信号：
        - K线下穿D线
        - K、D值在超买区
        """
        df = data.copy()
        
        n = self.params['n']
        m1 = self.params['m1']
        m2 = self.params['m2']
        oversold = self.params['oversold']
        overbought = self.params['overbought']
        
        # 计算KDJ
        df['k'], df['d'], df['j'] = self._calculate_kdj(
            df['high'], df['low'], df['close'], n, m1, m2
        )
        
        # 生成信号
        df['signal'] = 0
        
        # 买入：K线上穿D线且在超卖区
        buy_condition = (
            self.cross_above(df['k'], df['d']) &
            (df['k'] < oversold) &
            (df['d'] < oversold)
        )
        df.loc[buy_condition, 'signal'] = 1
        
        # 卖出：K线下穿D线且在超买区
        sell_condition = (
            self.cross_below(df['k'], df['d']) &
            (df['k'] > overbought) &
            (df['d'] > overbought)
        )
        df.loc[sell_condition, 'signal'] = -1
        
        return df


class VolumePriceStrategy(BaseStrategy):
    """
    量价策略
    
    参数：
    - volume_ma_window: 成交量均线周期（默认20）
    - price_change_threshold: 价格变化阈值（默认0.02）
    - volume_increase_threshold: 成交量放大倍数（默认2.0）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'volume_ma_window': 20,
            'price_change_threshold': 0.02,
            'volume_increase_threshold': 2.0
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_name(self) -> str:
        return "量价策略"
    
    def validate_params(self) -> bool:
        volume_window = self.params.get('volume_ma_window', 20)
        price_threshold = self.params.get('price_change_threshold', 0.02)
        volume_threshold = self.params.get('volume_increase_threshold', 2.0)
        
        return volume_window > 0 and price_threshold > 0 and volume_threshold > 0
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成信号
        
        买入信号：
        - 放量突破：成交量放大 + 价格上涨
        
        卖出信号：
        - 缩量下跌：成交量萎缩 + 价格下跌
        """
        df = data.copy()
        
        volume_window = self.params['volume_ma_window']
        price_threshold = self.params['price_change_threshold']
        volume_threshold = self.params['volume_increase_threshold']
        
        # 计算成交量均线
        df['volume_ma'] = df['volume'].rolling(window=volume_window).mean()
        
        # 计算成交量放大倍数
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # 计算价格变化
        df['price_change'] = df['close'].pct_change()
        
        # 生成信号
        df['signal'] = 0
        
        # 买入：放量上涨
        buy_condition = (
            (df['volume_ratio'] >= volume_threshold) &
            (df['price_change'] >= price_threshold)
        )
        df.loc[buy_condition, 'signal'] = 1
        
        # 卖出：缩量下跌
        sell_condition = (
            (df['volume_ratio'] <= 1/volume_threshold) &
            (df['price_change'] <= -price_threshold)
        )
        df.loc[sell_condition, 'signal'] = -1
        
        return df


class MultiFactorStrategy(BaseStrategy):
    """
    多因子组合策略
    
    组合多个技术指标进行综合判断
    
    参数：
    - factors: 因子列表 ['rsi', 'macd', 'volume', 'momentum']
    - weights: 因子权重（默认等权重）
    - buy_threshold: 买入阈值（默认0.6）
    - sell_threshold: 卖出阈值（默认-0.6）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'factors': ['rsi', 'macd', 'volume', 'momentum'],
            'weights': None,  # 等权重
            'buy_threshold': 0.6,
            'sell_threshold': -0.6,
            'rsi_window': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'volume_window': 20,
            'momentum_window': 10
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_name(self) -> str:
        return f"多因子策略（{len(self.params['factors'])}因子）"
    
    def validate_params(self) -> bool:
        factors = self.params.get('factors', [])
        buy_threshold = self.params.get('buy_threshold', 0.6)
        sell_threshold = self.params.get('sell_threshold', -0.6)
        
        return len(factors) > 0 and sell_threshold < buy_threshold
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成信号
        
        计算多个因子的得分，加权求和后判断买卖
        """
        df = data.copy()
        
        factors = self.params['factors']
        weights = self.params.get('weights')
        buy_threshold = self.params['buy_threshold']
        sell_threshold = self.params['sell_threshold']
        
        # 如果没有提供权重，使用等权重
        if weights is None:
            weights = [1.0 / len(factors)] * len(factors)
        
        # 计算各因子得分（-1到1之间）
        factor_scores = pd.DataFrame(index=df.index)
        
        for factor in factors:
            if factor == 'rsi':
                # RSI因子：超卖为正，超买为负
                rsi = self.rsi(df['close'], self.params['rsi_window'])
                # 转换到-1到1
                factor_scores['rsi'] = (50 - rsi) / 50
            
            elif factor == 'macd':
                # MACD因子：金叉为正，死叉为负
                macd_line, signal_line, _ = self.macd(
                    df['close'],
                    self.params['macd_fast'],
                    self.params['macd_slow'],
                    self.params['macd_signal']
                )
                # 根据MACD柱判断
                histogram = macd_line - signal_line
                factor_scores['macd'] = np.tanh(histogram / df['close'].std())
            
            elif factor == 'volume':
                # 成交量因子：放量上涨为正
                volume_ma = df['volume'].rolling(window=self.params['volume_window']).mean()
                volume_ratio = df['volume'] / volume_ma
                price_change = df['close'].pct_change()
                
                # 放量上涨为正，缩量下跌为负
                factor_scores['volume'] = np.tanh(
                    (volume_ratio - 1) * np.sign(price_change)
                )
            
            elif factor == 'momentum':
                # 动量因子
                momentum = df['close'].pct_change(self.params['momentum_window'])
                factor_scores['momentum'] = np.tanh(momentum * 10)
        
        # 计算综合得分
        df['composite_score'] = 0
        for i, factor in enumerate(factors):
            df['composite_score'] += factor_scores[factor] * weights[i]
        
        # 生成信号
        df['signal'] = 0
        
        # 买入：综合得分超过买入阈值
        df.loc[df['composite_score'] >= buy_threshold, 'signal'] = 1
        
        # 卖出：综合得分低于卖出阈值
        df.loc[df['composite_score'] <= sell_threshold, 'signal'] = -1
        
        return df


class TurtleStrategy(BaseStrategy):
    """
    海龟交易策略（简化版）
    
    参数：
    - entry_window: 入场周期（默认20）
    - exit_window: 出场周期（默认10）
    - atr_window: ATR周期（默认20）
    - risk_per_trade: 单笔风险比例（默认0.01）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'entry_window': 20,
            'exit_window': 10,
            'atr_window': 20,
            'risk_per_trade': 0.01
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
    
    def get_name(self) -> str:
        return "海龟策略"
    
    def validate_params(self) -> bool:
        entry = self.params.get('entry_window', 20)
        exit_w = self.params.get('exit_window', 10)
        
        return entry > 0 and exit_w > 0
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成信号
        
        买入：突破20日最高价
        卖出：跌破10日最低价
        """
        df = data.copy()
        
        entry_window = self.params['entry_window']
        exit_window = self.params['exit_window']
        
        # 计算突破价格
        df['entry_high'] = df['high'].rolling(window=entry_window).max().shift(1)
        df['exit_low'] = df['low'].rolling(window=exit_window).min().shift(1)
        
        # 计算ATR（用于止损）
        df['atr'] = self.atr(df['high'], df['low'], df['close'], self.params['atr_window'])
        
        # 生成信号
        df['signal'] = 0
        
        # 买入：突破入场高点
        df.loc[df['close'] > df['entry_high'], 'signal'] = 1
        
        # 卖出：跌破出场低点
        df.loc[df['close'] < df['exit_low'], 'signal'] = -1
        
        return df


# 导出策略类
__all__ = [
    'BollingerBandsStrategy',
    'KDJStrategy',
    'VolumePriceStrategy',
    'MultiFactorStrategy',
    'TurtleStrategy'
]
