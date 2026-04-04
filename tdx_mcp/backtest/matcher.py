# coding=utf-8
"""
订单撮合引擎

模拟订单成交，包括滑点和手续费
"""

from typing import Dict, Optional
from datetime import datetime


import pandas as pd


class OrderMatcher:
    """
    订单撮合引擎
    
    功能：
    - 支持市价单、限价单
    - 模拟滑点
    - 计算手续费
    """
    
    def __init__(self, 
                 commission_rate: float = 0.0003,  # 佣金率 0.03%
                 stamp_duty_rate: float = 0.0,     # 廱花税 0%（仅卖出）
                 transfer_fee_rate: float = 0.0,   # 过户费（仅沪市）
                 slippage_rate: float = 0.0):    # 滑点 0%（模拟买卖价差）
        """
        初始化撮合引擎
        
        Args:
            commission_rate: 佣金率（默认0.03%）
            stamp_duty_rate: 印花税率（默认1%，仅卖出）
            transfer_fee_rate: 过户费率（默认0%，仅沪市股票）
            slippage_rate: 滑点率（默认1%）
        """
        self.commission_rate = commission_rate
        self.stamp_duty_rate = stamp_duty_rate
        self.transfer_fee_rate = transfer_fee_rate
        self.slippage_rate = slippage_rate
    
    def match_order(self, 
                   order: Dict, 
                   current_price: float,
                   tick_data: Optional[Dict] = None) -> Dict:
        """
        撮合订单
        
        Args:
            order: 订单信息
            current_price: 当前价格
            tick_data: tick数据（可选，用于限价单撮合）
        
        Returns:
            Dict: 成交信息 {
                'success': bool,
                'executed_price': float,
                'executed_quantity': int,
                'slippage': float,
                'commission': float,
                'stamp_duty': float,
                'transfer_fee': float,
                'total_cost': float,
                'message': str
            }
        """
        stock_code = order['stock_code']
        direction = order['direction']
        quantity = order['quantity']
        price_type = order['price_type']
        limit_price = order.get('limit_price')
        
        # 滑点计算
        slippage = 0.0
        if self.slippage_rate > 0:
            slippage = current_price * self.slippage_rate
        
        # 执行价格
        if price_type == 'MARKET':
            # 市价单：使用当前价格 + 滑点
            if direction == 'BUY':
                executed_price = current_price + slippage
            else:
                executed_price = current_price - slippage
        elif price_type == 'LIMIT':
            # 限价单：检查价格是否匹配
            if limit_price is None:
                return {
                    'success': False,
                    'message': '限价单必须指定价格'
                }
            
            # 简化处理：如果当前价格触及限价，则成交
            if direction == 'BUY' and current_price > limit_price:
                return {
                    'success': False,
                    'message': f'当前价格{current_price}高于限价{limit_price}，未成交'
                }
            elif direction == 'SELL' and current_price < limit_price:
                return {
                    'success': False,
                    'message': f'当前价格{current_price}低于限价{limit_price}，未成交'
                }
            
            executed_price = limit_price
        else:
            return {
                'success': False,
                'message': f'不支持的价格类型: {price_type}'
            }
        
        # 计算手续费
        commission = executed_price * quantity * self.commission_rate
        
        # 壱花税（仅卖出）
        stamp_duty = 0.0
        if direction == 'SELL':
            stamp_duty = executed_price * quantity * self.stamp_duty_rate
        
        # 过户费（仅沪市股票）
        transfer_fee = 0.0
        if stock_code.endswith('.SH'):
            transfer_fee = executed_price * quantity * self.transfer_fee_rate / 10000
        
        # 总成本
        if direction == 'BUY':
            total_cost = executed_price * quantity + commission + transfer_fee
        else:
            total_cost = executed_price * quantity - commission - stamp_duty - transfer_fee
        
        return {
            'success': True,
            'executed_price': round(executed_price, 2),
            'executed_quantity': quantity,
            'slippage': round(slippage, 2),
            'commission': round(commission, 2),
            'stamp_duty': round(stamp_duty, 2),
            'transfer_fee': round(transfer_fee, 2),
            'total_cost': round(total_cost, 2),
            'message': '成交成功'
        }
    
    def calculate_commission(self, price: float, quantity: int) -> float:
        """
        计算手续费（简化版）
        
        Args:
            price: 价格
            quantity: 数量
        
        Returns:
            float: 手续费
        """
        return price * quantity * self.commission_rate


class TickMatcher(OrderMatcher):
    """
    Tick级订单撮合引擎
    
    支持逐tick精确撮合
    """
    
    def match_tick_order(self, 
                        order: Dict, 
                        tick_data: Dict) -> Dict:
        """
        基于tick数据撮合订单
        
        Args:
            order: 订单信息
            tick_data: tick数据
        
        Returns:
            Dict: 成交信息
        """
        tick_price = tick_data['price']
        tick_volume = tick_data['volume']
        
        # 使用父类方法撮合
        result = self.match_order(order, tick_price, tick_data)
        
        # 额外检查：tick成交量是否足够
        if result['success']:
            if order['quantity'] > tick_volume:
                # 部分成交
                result['executed_quantity'] = tick_volume
                result['message'] = f'部分成交：委托{order["quantity"]}股，成交{tick_volume}股'
        
        return result
