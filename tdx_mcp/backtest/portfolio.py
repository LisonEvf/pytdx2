# coding=utf-8
"""
持仓管理

管理账户持仓、资金、交易记录
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


class Portfolio:
    """
    持仓管理器

    功能：
    - 管理持仓数量和成本
    - 记录交易流水
    - 计算账户资产
    """

    def __init__(self, initial_capital: float = 1000000.0):
        """
        初始化持仓管理器

        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.available_cash = initial_capital

        # 持仓 {stock_code: {'amount': int, 'avg_cost': float, 'market_value': float}}
        self.positions: Dict[str, Dict] = {}

        # 交易记录
        self.trades: List[Dict] = []

        # 每日净值记录
        self.daily_values: List[Dict] = []

    # ==================== 持仓管理 ====================

    def get_position(self, stock_code: str) -> int:
        """
        获取持仓数量

        Args:
            stock_code: 股票代码

        Returns:
            int: 持仓数量
        """
        return self.positions.get(stock_code, {}).get('amount', 0)

    def get_all_positions(self) -> Dict[str, int]:
        """
        获取所有持仓

        Returns:
            Dict: {股票代码: 持仓数量}
        """
        return {code: pos['amount'] for code, pos in self.positions.items() if pos['amount'] > 0}

    def update_position(self, stock_code: str, amount: int, price: float):
        """
        更新持仓

        Args:
            stock_code: 股票代码
            amount: 成交数量（正数买入，负数卖出）
            price: 成交价格
        """
        current_pos = self.positions.get(stock_code, {'amount': 0, 'avg_cost': 0.0})
        current_amount = current_pos['amount']
        current_cost = current_pos['avg_cost']

        if amount > 0:
            # 买入，更新平均成本
            new_amount = current_amount + amount
            new_cost = (current_amount * current_cost + amount * price) / new_amount if new_amount > 0 else 0

            self.positions[stock_code] = {
                'amount': new_amount,
                'avg_cost': new_cost,
                'market_value': new_amount * price
            }
        elif amount < 0:
            # 卖出，保持成本不变
            new_amount = current_amount + amount  # amount是负数

            if new_amount <= 0:
                # 清仓
                if stock_code in self.positions:
                    del self.positions[stock_code]
            else:
                self.positions[stock_code] = {
                    'amount': new_amount,
                    'avg_cost': current_cost,
                    'market_value': new_amount * price
                }

    # ==================== 资金管理 ====================

    def update_cash(self, delta: float):
        """
        更新可用资金

        Args:
            delta: 资金变化（正数增加，负数减少）
        """
        self.available_cash += delta

    def can_afford(self, amount: float) -> bool:
        """
        检查是否有足够资金

        Args:
            amount: 需要的金额

        Returns:
            bool: 是否有足够资金
        """
        return self.available_cash >= amount

    # ==================== 交易记录 ====================

    def record_trade(self, trade: Dict):
        """
        记录交易

        Args:
            trade: 交易记录
            {
                'datetime': datetime,
                'stock_code': str,
                'direction': 'BUY' | 'SELL',
                'quantity': int,
                'price': float,
                'amount': float,
                'commission': float,
                'slippage': float
            }
        """
        self.trades.append(trade)

    def get_trades(self, stock_code: str = None) -> List[Dict]:
        """
        获取交易记录

        Args:
            stock_code: 股票代码（可选，不指定则返回所有）

        Returns:
            List: 交易记录列表
        """
        if stock_code:
            return [t for t in self.trades if t['stock_code'] == stock_code]
        return self.trades

    # ==================== 资产计算 ====================

    def total_value(self, current_prices: Dict[str, float]) -> float:
        """
        计算总资产

        Args:
            current_prices: 当前价格字典 {股票代码: 价格}

        Returns:
            float: 总资产（现金+持仓市值）
        """
        position_value = 0
        for stock_code, pos in self.positions.items():
            price = current_prices.get(stock_code, pos['avg_cost'])
            position_value += pos['amount'] * price

        return self.available_cash + position_value

    def market_value(self, stock_code: str, current_price: float) -> float:
        """
        计算单只股票市值

        Args:
            stock_code: 股票代码
            current_price: 当前价格

        Returns:
            float: 持仓市值
        """
        amount = self.get_position(stock_code)
        return amount * current_price

    # ==================== 净值记录 ====================

    def record_daily_value(self, date, current_prices: Dict[str, float]):
        """
        记录每日净值

        Args:
            date: 日期
            current_prices: 当前价格字典
        """
        total = self.total_value(current_prices)
        self.daily_values.append({
            'date': date,
            'total_value': total,
            'cash': self.available_cash,
            'position_value': total - self.available_cash
        })

    def get_daily_values(self) -> pd.DataFrame:
        """
        获取每日净值记录

        Returns:
            DataFrame: 净值数据
        """
        return pd.DataFrame(self.daily_values)

    # ==================== 统计分析 ====================

    def get_position_count(self) -> int:
        """获取持仓股票数量"""
        return len([pos for pos in self.positions.values() if pos['amount'] > 0])

    def get_trade_count(self) -> int:
        """获取交易次数"""
        return len(self.trades)

    def get_profit_loss(self, current_prices: Dict[str, float]) -> float:
        """
        计算总盈亏

        Args:
            current_prices: 当前价格字典

        Returns:
            float: 总盈亏
        """
        return self.total_value(current_prices) - self.initial_capital

    def get_profit_loss_pct(self, current_prices: Dict[str, float]) -> float:
        """
        计算收益率

        Returns:
            float: 收益率（%）
        """
        pnl = self.get_profit_loss(current_prices)
        return (pnl / self.initial_capital) * 100
