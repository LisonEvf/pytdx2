# coding=utf-8
"""
ContextInfo模拟

提供QMT兼容的策略上下文接口
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
from .portfolio import Portfolio


class ContextInfo:
    """
    模拟QMT ContextInfo对象

    提供策略运行时的上下文环境，包括：
    - 历史数据查询
    - 持仓管理
    - 下单接口
    - 账户信息
    """

    def __init__(self, backtest_engine, start_date: date, end_date: date):
        """
        初始化上下文

        Args:
            backtest_engine: 回测引擎实例
            start_date: 回测开始日期
            end_date: 回测结束日期
        """
        self.engine = backtest_engine
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = start_date
        self.current_time = None

        # 用户自定义变量存储
        self._user_vars = {}

        # 持仓管理
        self.portfolio = Portfolio(initial_capital=1000000.0)

    # ==================== 用户变量管理 ====================

    def __setattr__(self, name, value):
        """支持直接赋值"""
        if name in ['engine', 'start_date', 'end_date', 'current_date', 'current_time', 'portfolio', '_user_vars']:
            object.__setattr__(self, name, value)
        else:
            self._user_vars[name] = value

    def __getattr__(self, name):
        """支持直接读取"""
        if name in self._user_vars:
            return self._user_vars[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    # ==================== 数据查询接口 ====================

    def history(self, field: str, length: int, stock_code: str = None) -> List[Any]:
        """
        获取历史数据（QMT兼容接口）

        Args:
            field: 字段名（'open', 'high', 'low', 'close', 'volume'）
            length: 数据长度
            stock_code: 股票代码（可选，默认使用context.stock）

        Returns:
            List: 历史数据列表

        Example:
            closes = context.history('close', 20)
        """
        stock = stock_code or self._user_vars.get('stock')
        if not stock:
            raise ValueError("未指定股票代码")

        # 调用引擎获取历史数据
        return self.engine.get_history_data(stock, field, length, self.current_date)

    def get_market_data(self, field: str, stock_code: str = None) -> Any:
        """
        获取当前市场数据（QMT兼容接口）

        Args:
            field: 字段名
            stock_code: 股票代码

        Returns:
            当前值
        """
        stock = stock_code or self._user_vars.get('stock')
        if not stock:
            raise ValueError("未指定股票代码")

        # 调用引擎获取当前数据
        return self.engine.get_current_data(stock, field, self.current_date)

    def get_tick_data(self, stock_code: str = None) -> List[Dict]:
        """
        获取tick数据（QMT兼容接口）

        Args:
            stock_code: 股票代码

        Returns:
            List[Dict]: tick数据列表
        """
        stock = stock_code or self._user_vars.get('stock')
        if not stock:
            raise ValueError("未指定股票代码")

        return self.engine.get_tick_data(stock, self.current_date)

    # ==================== 持仓查询接口 ====================

    def position(self, stock_code: str = None) -> int:
        """
        查询持仓数量

        Args:
            stock_code: 股票代码

        Returns:
            int: 持仓股数
        """
        stock = stock_code or self._user_vars.get('stock')
        if not stock:
            raise ValueError("未指定股票代码")

        return self.portfolio.get_position(stock)

    def positions(self) -> Dict[str, int]:
        """
        查询所有持仓

        Returns:
            Dict: {股票代码: 持仓数量}
        """
        return self.portfolio.get_all_positions()

    def available_cash(self) -> float:
        """
        查询可用资金

        Returns:
            float: 可用资金
        """
        return self.portfolio.available_cash

    def total_value(self) -> float:
        """
        查询总资产

        Returns:
            float: 总资产（现金+持仓市值）
        """
        return self.portfolio.total_value(self.engine.get_current_prices())

    # ==================== 下单接口（QMT兼容） ====================

    def order_target(self, stock_code: str, amount: int):
        """
        调整持仓到目标数量（QMT兼容接口）

        Args:
            stock_code: 股票代码（如 '000001.SZ'）
            amount: 目标持仓数量

        Example:
            context.order_target('000001.SZ', 100)  # 调整到100股
            context.order_target('000001.SZ', 0)    # 清仓
        """
        if not stock_code:
            stock_code = self._user_vars.get('stock')
        if not stock_code:
            raise ValueError("未指定股票代码")

        current_pos = self.portfolio.get_position(stock_code)
        delta = amount - current_pos

        if delta > 0:
            # 买入
            self.engine.place_order(
                stock_code=stock_code,
                direction='BUY',
                quantity=delta,
                price_type='MARKET',  # 市价单
                context=self
            )
        elif delta < 0:
            # 卖出
            self.engine.place_order(
                stock_code=stock_code,
                direction='SELL',
                quantity=abs(delta),
                price_type='MARKET',
                context=self
            )

    def order_target_percent(self, stock_code: str, percent: float):
        """
        调整持仓到目标百分比（QMT兼容接口）

        Args:
            stock_code: 股票代码
            percent: 目标仓位比例（0.0-1.0）

        Example:
            context.order_target_percent('000001.SZ', 0.5)  # 调整到50%仓位
        """
        if not stock_code:
            stock_code = self._user_vars.get('stock')
        if not stock_code:
            raise ValueError("未指定股票代码")

        total_value = self.total_value()
        target_value = total_value * percent
        current_price = self.engine.get_current_prices().get(stock_code, 0)

        if current_price == 0:
            return

        target_amount = int(target_value / current_price / 100) * 100  # 向下取整到100股

        self.order_target(stock_code, target_amount)

    def order_target_value(self, stock_code: str, value: float):
        """
        调整持仓到目标市值（QMT兼容接口）

        Args:
            stock_code: 股票代码
            value: 目标市值
        """
        if not stock_code:
            stock_code = self._user_vars.get('stock')
        if not stock_code:
            raise ValueError("未指定股票代码")

        current_price = self.engine.get_current_prices().get(stock_code, 0)
        if current_price == 0:
            return

        target_amount = int(value / current_price / 100) * 100

        self.order_target(stock_code, target_amount)

    # ==================== 辅助接口 ====================

    def log(self, msg: str):
        """
        输出日志（QMT兼容接口）

        Args:
            msg: 日志消息
        """
        print(f"[{self.current_date}] {msg}")

    def plot(self, name: str, value: float, color: str = 'blue'):
        """
        绘制指标曲线（QMT兼容接口，回测时忽略）

        Args:
            name: 指标名称
            value: 指标值
            color: 颜色
        """
        # 回测模式下不绘制，仅记录
        pass
