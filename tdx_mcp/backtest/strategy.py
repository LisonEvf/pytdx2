# coding=utf-8
"""
策略基类

提供QMT兼容的策略接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseStrategy(ABC):
    """
    策略基类（兼容QMT接口）

    示例:
        class MyStrategy(BaseStrategy):
            def init(self, context):
                context.stock = '000001.SZ'

            def handle_bar(self, context, bar):
                close = bar['close']
                if close > context.ma20:
                    context.order_target(context.stock, 100)
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.context = None

    @abstractmethod
    def init(self, context: 'ContextInfo'):
        """
        策略初始化（QMT兼容接口）

        Args:
            context: 策略上下文（模拟QMT ContextInfo）
        """
        pass

    @abstractmethod
    def handle_bar(self, context: 'ContextInfo', bar: Dict[str, Any]):
        """
        K线事件处理（QMT兼容接口）

        Args:
            context: 策略上下文
            bar: K线数据 {'open', 'high', 'low', 'close', 'volume', 'datetime'}
        """
        pass

    def handle_tick(self, context: 'ContextInfo', tick: Dict[str, Any]):
        """
        Tick事件处理（可选实现）

        Args:
            context: 策略上下文
            tick: Tick数据 {'price', 'volume', 'time', 'action'}
        """
        # 默认实现：空操作
        pass

    def on_order_filled(self, context: 'ContextInfo', order: Dict[str, Any]):
        """
        订单成交回调

        Args:
            context: 策略上下文
            order: 成交订单信息
        """
        pass

    def on_backtest_end(self, context: 'ContextInfo'):
        """
        回测结束回调
        """
        pass


class SimpleStrategy(BaseStrategy):
    """
    简单策略模板（用于快速测试）
    """

    def __init__(self, stock_code: str, fast_period: int = 5, slow_period: int = 20):
        super().__init__()
        self.stock_code = stock_code
        self.fast_period = fast_period
        self.slow_period = slow_period

    def init(self, context):
        """初始化策略"""
        context.stock = self.stock_code
        context.fast_ma = []
        context.slow_ma = []

    def handle_bar(self, context, bar):
        """处理K线事件"""
        # 计算均线
        closes = context.history('close', self.slow_period)
        if len(closes) < self.slow_period:
            return

        fast_ma = sum(closes[-self.fast_period:]) / self.fast_period
        slow_ma = sum(closes[-self.slow_period:]) / self.slow_period

        # 金叉买入，死叉卖出
        current_pos = context.position(self.stock_code)

        if fast_ma > slow_ma and current_pos == 0:
            # 金叉买入
            context.order_target_percent(self.stock_code, 1.0)
        elif fast_ma < slow_ma and current_pos > 0:
            # 死叉卖出
            context.order_target(self.stock_code, 0)
