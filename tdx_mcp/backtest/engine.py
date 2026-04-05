# coding=utf-8
"""
回测引擎模块
功能：
1. 历史数据获取
2. 回测执行引擎
3. 订单管理
4. 持仓管理
5. 回测结果生成
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .strategy_base import BaseStrategy


class BacktestEngine:
    """
    回测引擎
    
    功能：
    1. 执行策略回测
    2. 管理账户资金
    3. 计算交易成本
    4. 生成回测报告
    """
    
    def __init__(
        self,
        initial_capital: float = 1000000,
        commission_rate: float = 0.0003,
        slippage_rate: float = 0.0001,
        position_size: float = 0.95  # 仓位比例
    ):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage_rate: 滑点率
            position_size: 仓位比例
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.position_size = position_size
        
        # 账户状态
        self.cash = initial_capital
        self.position = 0  # 持仓数量
        self.position_value = 0  # 持仓市值
        
        # 交易记录
        self.trades = []
        self.daily_values = []
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy: BaseStrategy,
        stock_code: str = 'UNKNOWN'
    ) -> Dict[str, Any]:
        """
        执行回测
        
        Args:
            data: 股票历史数据（必须包含date, open, high, low, close, volume列）
            strategy: 策略实例
            stock_code: 股票代码
        
        Returns:
            回测结果字典
        """
        # 重置状态
        self.cash = self.initial_capital
        self.position = 0
        self.position_value = 0
        self.trades = []
        self.daily_values = []
        
        # 生成信号
        df = strategy.generate_signals(data)
        
        # 遍历每一天
        for idx, row in df.iterrows():
            date = row.get('date', idx)
            open_price = row['open']
            high = row['high']
            low = row['low']
            close = row['close']
            volume = row['volume']
            signal = row.get('signal', 0)
            
            # 执行交易
            if signal == 1 and self.position == 0:
                # 买入
                available_cash = self.cash * self.position_size
                buy_price = open_price * (1 + self.slippage_rate)  # 考虑滑点
                shares = int(available_cash / buy_price / 100) * 100  # 买整手
                
                if shares > 0:
                    cost = shares * buy_price
                    commission = cost * self.commission_rate
                    total_cost = cost + commission
                    
                    self.position = shares
                    self.cash -= total_cost
                    
                    # 记录交易
                    self.trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': buy_price,
                        'shares': shares,
                        'commission': commission,
                        'cash_after': self.cash
                    })
            
            elif signal == -1 and self.position > 0:
                # 卖出
                sell_price = open_price * (1 - self.slippage_rate)  # 考虑滑点
                shares = self.position
                
                revenue = shares * sell_price
                commission = revenue * self.commission_rate
                total_revenue = revenue - commission
                
                self.cash += total_revenue
                self.position = 0
                
                # 记录交易
                self.trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': sell_price,
                    'shares': shares,
                    'commission': commission,
                    'cash_after': self.cash
                })
            
            # 计算当日市值
            self.position_value = self.position * close
            total_value = self.cash + self.position_value
            
            # 记录每日市值
            self.daily_values.append({
                'date': date,
                'cash': self.cash,
                'position': self.position,
                'position_value': self.position_value,
                'total_value': total_value,
                'close': close
            })
        
        # 计算绩效指标
        performance = self._calculate_performance()
        
        return {
            'stock_code': stock_code,
            'strategy_name': strategy.get_name(),
            'strategy_params': strategy.get_params(),
            'initial_capital': self.initial_capital,
            'final_capital': performance['final_capital'],
            'total_return': performance['total_return'],
            'annual_return': performance['annual_return'],
            'sharpe_ratio': performance['sharpe_ratio'],
            'max_drawdown': performance['max_drawdown'],
            'win_rate': performance['win_rate'],
            'total_trades': len(self.trades),
            'trades': self.trades,
            'daily_values': self.daily_values,
            'performance': performance
        }
    
    def _calculate_performance(self) -> Dict[str, Any]:
        """计算绩效指标"""
        if not self.daily_values:
            return {
                'final_capital': self.initial_capital,
                'total_return': 0,
                'annual_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0
            }
        
        # 转换为DataFrame
        df = pd.DataFrame(self.daily_values)
        
        # 最终市值
        final_capital = df['total_value'].iloc[-1]
        
        # 总收益率
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        
        # 年化收益率（假设数据是日线）
        days = len(df)
        annual_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0
        
        # 计算日收益率
        df['daily_return'] = df['total_value'].pct_change()
        
        # 夏普比率（假设无风险利率为3%）
        risk_free_rate = 0.03 / 252
        excess_returns = df['daily_return'] - risk_free_rate
        
        if excess_returns.std() > 0:
            sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # 最大回撤
        df['cumulative_max'] = df['total_value'].cummax()
        df['drawdown'] = (df['cumulative_max'] - df['total_value']) / df['cumulative_max']
        max_drawdown = df['drawdown'].max()
        
        # 胜率
        if self.trades:
            winning_trades = 0
            total_pairs = 0
            
            # 计算配对交易的盈亏
            for i in range(0, len(self.trades) - 1, 2):
                if i + 1 < len(self.trades):
                    buy_trade = self.trades[i]
                    sell_trade = self.trades[i + 1]
                    
                    if buy_trade['type'] == 'BUY' and sell_trade['type'] == 'SELL':
                        profit = (sell_trade['price'] - buy_trade['price']) * buy_trade['shares']
                        if profit > 0:
                            winning_trades += 1
                        total_pairs += 1
            
            win_rate = winning_trades / total_pairs if total_pairs > 0 else 0
        else:
            win_rate = 0
        
        return {
            'final_capital': final_capital,
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate
        }


def run_multi_stock_backtest(
    stock_data: Dict[str, pd.DataFrame],
    strategy: BaseStrategy,
    initial_capital: float = 1000000,
    **engine_params
) -> Dict[str, Any]:
    """
    多股票回测
    
    Args:
        stock_data: 股票数据字典 {股票代码: DataFrame}
        strategy: 策略实例
        initial_capital: 初始资金
        engine_params: 引擎参数
    
    Returns:
        回测结果字典
    """
    results = {}
    
    for stock_code, data in stock_data.items():
        engine = BacktestEngine(initial_capital=initial_capital, **engine_params)
        result = engine.run_backtest(data, strategy, stock_code)
        results[stock_code] = result
    
    # 计算平均绩效
    if results:
        avg_return = np.mean([r['total_return'] for r in results.values()])
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in results.values()])
        avg_drawdown = np.mean([r['max_drawdown'] for r in results.values()])
        
        return {
            'strategy_name': strategy.get_name(),
            'stock_count': len(results),
            'avg_return': avg_return,
            'avg_sharpe_ratio': avg_sharpe,
            'avg_max_drawdown': avg_drawdown,
            'results': results
        }
    
    return {}


# 导出类和函数
__all__ = [
    'BacktestEngine',
    'run_multi_stock_backtest'
]
