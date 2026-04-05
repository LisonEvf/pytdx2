# coding=utf-8
"""
风险管理模块
功能：
1. 止损止盈管理
2. 移动止损
3. 仓位管理
4. 风险控制
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np


class RiskManager:
    """
    风险管理器
    
    支持多种风险控制策略：
    - 固定止损止盈
    - 移动止损（Trailing Stop）
    - ATR止损
    - 最大持仓时间
    - 最大回撤控制
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化风险管理器
        
        Args:
            params: 风控参数
        """
        self.params = params or {}
        
        # 止损止盈参数
        self.stop_loss_pct = self.params.get('stop_loss_pct', 0.05)  # 止损比例（5%）
        self.take_profit_pct = self.params.get('take_profit_pct', 0.15)  # 止盈比例（15%）
        
        # 移动止损参数
        self.trailing_stop_pct = self.params.get('trailing_stop_pct', 0.03)  # 移动止损比例（3%）
        self.trailing_stop_trigger = self.params.get('trailing_stop_trigger', 0.05)  # 触发移动止损的盈利比例（5%）
        
        # ATR止损参数
        self.atr_multiplier = self.params.get('atr_multiplier', 2.0)  # ATR倍数
        
        # 持仓时间控制
        self.max_holding_days = self.params.get('max_holding_days', 20)  # 最大持仓天数
        
        # 回撤控制
        self.max_drawdown_pct = self.params.get('max_drawdown_pct', 0.2)  # 最大回撤比例（20%）
        
        # 仓位管理
        self.position_sizing = self.params.get('position_sizing', 'fixed')  # fixed/kelly/volatility
        self.risk_per_trade = self.params.get('risk_per_trade', 0.02)  # 单笔风险比例（2%）
        
        # 状态跟踪
        self.position_info = None
        self.high_price = None
        self.entry_date = None
        self.peak_value = None
    
    def on_buy(
        self,
        entry_price: float,
        entry_date: datetime,
        atr: float = None,
        capital: float = None
    ) -> Dict[str, Any]:
        """
        买入时初始化风控参数
        
        Args:
            entry_price: 买入价格
            entry_date: 买入日期
            atr: ATR值（可选）
            capital: 当前资金（可选）
        
        Returns:
            风控参数字典
        """
        self.position_info = {
            'entry_price': entry_price,
            'entry_date': entry_date,
            'atr': atr,
            'capital': capital or 0,
            'trailing_stop_active': False,
            'trailing_stop_price': None
        }
        
        self.high_price = entry_price
        self.entry_date = entry_date
        
        # 计算止损止盈价格
        stop_loss_price = entry_price * (1 - self.stop_loss_pct)
        take_profit_price = entry_price * (1 + self.take_profit_pct)
        
        # ATR止损
        atr_stop_price = None
        if atr:
            atr_stop_price = entry_price - (atr * self.atr_multiplier)
        
        return {
            'entry_price': entry_price,
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price,
            'atr_stop_price': atr_stop_price,
            'trailing_stop_pct': self.trailing_stop_pct,
            'max_holding_days': self.max_holding_days
        }
    
    def check_sell_signal(
        self,
        current_price: float,
        current_date: datetime,
        current_value: float = None,
        high_price: float = None
    ) -> Tuple[bool, str]:
        """
        检查是否需要卖出
        
        Args:
            current_price: 当前价格
            current_date: 当前日期
            current_value: 当前总市值（可选）
            high_price: 持仓期间最高价（可选）
        
        Returns:
            (是否卖出, 卖出原因)
        """
        if not self.position_info:
            return False, ""
        
        entry_price = self.position_info['entry_price']
        entry_date = self.position_info['entry_date']
        atr = self.position_info['atr']
        
        # 更新最高价
        if high_price:
            self.high_price = max(self.high_price, high_price)
        else:
            self.high_price = max(self.high_price, current_price)
        
        # 1. 检查固定止损
        stop_loss_price = entry_price * (1 - self.stop_loss_pct)
        if current_price <= stop_loss_price:
            return True, f"触发止损（-{-self.stop_loss_pct*100:.1f}%）"
        
        # 2. 检查固定止盈
        take_profit_price = entry_price * (1 + self.take_profit_pct)
        if current_price >= take_profit_price:
            return True, f"触发止盈（+{self.take_profit_pct*100:.1f}%）"
        
        # 3. 检查ATR止损
        if atr:
            atr_stop_price = entry_price - (atr * self.atr_multiplier)
            if current_price <= atr_stop_price:
                return True, f"触发ATR止损（{self.atr_multiplier}倍ATR）"
        
        # 4. 检查移动止损
        profit_pct = (current_price - entry_price) / entry_price
        
        # 触发移动止损
        if profit_pct >= self.trailing_stop_trigger:
            self.position_info['trailing_stop_active'] = True
            trailing_stop_price = self.high_price * (1 - self.trailing_stop_pct)
            self.position_info['trailing_stop_price'] = trailing_stop_price
        
        # 检查移动止损
        if self.position_info['trailing_stop_active']:
            trailing_stop_price = self.high_price * (1 - self.trailing_stop_pct)
            if current_price <= trailing_stop_price:
                return True, f"触发移动止损（最高价-{self.trailing_stop_pct*100:.1f}%）"
        
        # 5. 检查持仓时间
        if self.max_holding_days:
            holding_days = (current_date - entry_date).days
            if holding_days >= self.max_holding_days:
                return True, f"持仓时间过长（{holding_days}天）"
        
        # 6. 检查最大回撤
        if current_value and self.peak_value:
            drawdown = (self.peak_value - current_value) / self.peak_value
            if drawdown >= self.max_drawdown_pct:
                return True, f"触发最大回撤控制（{drawdown*100:.1f}%）"
        
        # 更新峰值
        if current_value:
            if not self.peak_value or current_value > self.peak_value:
                self.peak_value = current_value
        
        return False, ""
    
    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss_price: float = None,
        atr: float = None
    ) -> int:
        """
        计算仓位大小
        
        Args:
            capital: 可用资金
            entry_price: 买入价格
            stop_loss_price: 止损价格（可选）
            atr: ATR值（可选）
        
        Returns:
            建议买入股数
        """
        if self.position_sizing == 'fixed':
            # 固定仓位
            position_value = capital * self.risk_per_trade
            shares = int(position_value / entry_price / 100) * 100
            return shares
        
        elif self.position_sizing == 'kelly':
            # 凯利公式（简化版，需要历史胜率数据）
            # 这里使用固定比例作为简化
            position_value = capital * self.risk_per_trade * 2
            shares = int(position_value / entry_price / 100) * 100
            return shares
        
        elif self.position_sizing == 'volatility':
            # 波动率调整仓位
            if atr:
                # ATR越大，仓位越小
                volatility = atr / entry_price
                risk_adjusted = self.risk_per_trade / volatility
                position_value = capital * min(risk_adjusted, 0.95)
                shares = int(position_value / entry_price / 100) * 100
                return shares
            else:
                # 无ATR数据，使用固定仓位
                position_value = capital * self.risk_per_trade
                shares = int(position_value / entry_price / 100) * 100
                return shares
        
        else:
            # 默认固定仓位
            position_value = capital * self.risk_per_trade
            shares = int(position_value / entry_price / 100) * 100
            return shares
    
    def on_sell(self):
        """卖出时重置风控状态"""
        self.position_info = None
        self.high_price = None
        self.entry_date = None
    
    def get_risk_report(self) -> Dict[str, Any]:
        """生成风险报告"""
        if not self.position_info:
            return {
                'status': 'no_position',
                'message': '当前无持仓'
            }
        
        entry_price = self.position_info['entry_price']
        trailing_active = self.position_info['trailing_stop_active']
        trailing_price = self.position_info['trailing_stop_price']
        
        return {
            'status': 'holding',
            'entry_price': entry_price,
            'high_price': self.high_price,
            'profit_pct': (self.high_price - entry_price) / entry_price if entry_price else 0,
            'trailing_stop_active': trailing_active,
            'trailing_stop_price': trailing_price,
            'stop_loss_price': entry_price * (1 - self.stop_loss_pct),
            'take_profit_price': entry_price * (1 + self.take_profit_pct)
        }


class PortfolioRiskManager:
    """
    组合风险管理器
    
    管理多个持仓的整体风险
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化组合风险管理器
        
        Args:
            params: 组合风控参数
        """
        self.params = params or {}
        
        # 组合参数
        self.max_positions = self.params.get('max_positions', 10)  # 最大持仓数量
        self.max_single_position_pct = self.params.get('max_single_position_pct', 0.2)  # 单只股票最大仓位比例
        self.max_sector_pct = self.params.get('max_sector_pct', 0.4)  # 单行业最大仓位比例
        
        # 持仓记录
        self.positions = {}  # {stock_code: position_info}
        self.sector_map = {}  # {stock_code: sector}
    
    def can_add_position(
        self,
        stock_code: str,
        sector: str = None
    ) -> Tuple[bool, str]:
        """
        检查是否可以新增持仓
        
        Args:
            stock_code: 股票代码
            sector: 所属行业（可选）
        
        Returns:
            (是否可以买入, 原因)
        """
        # 检查持仓数量
        if len(self.positions) >= self.max_positions:
            return False, f"已达最大持仓数量（{self.max_positions}只）"
        
        # 检查是否已持有
        if stock_code in self.positions:
            return False, f"已持有{stock_code}"
        
        # 检查行业集中度
        if sector:
            sector_positions = [s for s, sec in self.sector_map.items() if sec == sector]
            if len(sector_positions) >= self.max_positions * self.max_sector_pct:
                return False, f"{sector}行业持仓过多"
        
        return True, "可以买入"
    
    def add_position(
        self,
        stock_code: str,
        shares: int,
        price: float,
        sector: str = None
    ):
        """添加持仓"""
        self.positions[stock_code] = {
            'shares': shares,
            'price': price,
            'value': shares * price
        }
        
        if sector:
            self.sector_map[stock_code] = sector
    
    def remove_position(self, stock_code: str):
        """移除持仓"""
        if stock_code in self.positions:
            del self.positions[stock_code]
        
        if stock_code in self.sector_map:
            del self.sector_map[stock_code]
    
    def get_portfolio_risk(self) -> Dict[str, Any]:
        """获取组合风险报告"""
        if not self.positions:
            return {
                'total_positions': 0,
                'total_value': 0,
                'sector_concentration': {}
            }
        
        # 计算总市值
        total_value = sum(p['value'] for p in self.positions.values())
        
        # 计算行业集中度
        sector_values = {}
        for stock_code, position in self.positions.items():
            sector = self.sector_map.get(stock_code, 'Unknown')
            sector_values[sector] = sector_values.get(sector, 0) + position['value']
        
        # 计算集中度比例
        sector_concentration = {
            sector: value / total_value if total_value > 0 else 0
            for sector, value in sector_values.items()
        }
        
        return {
            'total_positions': len(self.positions),
            'total_value': total_value,
            'sector_concentration': sector_concentration,
            'positions': self.positions
        }


# 导出类
__all__ = [
    'RiskManager',
    'PortfolioRiskManager'
]
