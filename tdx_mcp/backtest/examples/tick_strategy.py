#!/usr/bin/env python3
# coding=utf-8
"""
Tick级策略示例

演示tick级回测
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import date
from tdx_mcp.backtest.strategy import BaseStrategy
from tdx_mcp.backtest.engine import BacktestEngine


class TickStrategy(BaseStrategy):
    """
    Tick级策略
    
    策略逻辑：
    - 监控大单买入 → 跟随买入
    - 监控大单卖出 → 跟随卖出
    """
    
    def __init__(self, stock_code: str, large_order_threshold: int = 100000):
        """
        初始化
        
        Args:
            stock_code: 股票代码
            large_order_threshold: 大单阈值（股数）
        """
        super().__init__()
        self.stock_code = stock_code
        self.large_order_threshold = large_order_threshold
    
    def init(self, context):
        """初始化"""
        context.stock = self.stock_code
        context.large_buy_volume = 0
        context.large_sell_volume = 0
        context.last_tick_time = None
        
        context.log(f"初始化Tick策略: {self.stock_code}, 大单阈值{self.large_order_threshold}股")
    
    def handle_bar(self, context, bar):
        """K线处理（Tick策略通常不使用）"""
        pass
    
    def handle_tick(self, context, tick):
        """Tick事件处理"""
        # 解析tick数据
        price = tick['price']
        volume = tick['volume']
        action = tick.get('action', 'NEUTRAL')  # BUY/SELL/NEUTRAL
        
        # 更新统计
        if volume >= self.large_order_threshold:
            if action == 'BUY':
                context.large_buy_volume += volume
                context.log(f"大单买入: {volume}股 @ {price}")
            elif action == 'SELL':
                context.large_sell_volume += volume
                context.log(f"大单卖出: {volume}股 @ {price}")
        
        # 交易逻辑
        current_pos = context.position(self.stock_code)
        
        # 大单买入累计超过阈值 → 买入
        if context.large_buy_volume > 500000 and current_pos == 0:
            context.order_target_percent(self.stock_code, 0.8)
            context.log(f"跟随大单买入: 累计买入{context.large_buy_volume}股")
            context.large_buy_volume = 0
            context.large_sell_volume = 0
        
        # 大单卖出累计超过阈值 → 卖出
        elif context.large_sell_volume > 500000 and current_pos > 0:
            context.order_target(self.stock_code, 0)
            context.log(f"跟随大单卖出: 累计卖出{context.large_sell_volume}股")
            context.large_buy_volume = 0
            context.large_sell_volume = 0


def main():
    """运行tick级回测"""
    # 创建引擎
    engine = BacktestEngine(
        initial_capital=1000000.0,
        commission_rate=0.3,
        stamp_duty_rate=1.0,
        slippage_rate=0.1
    )
    
    # 创建策略
    strategy = TickStrategy(
        stock_code='000001.SZ',
        large_order_threshold=100000  # 10万股为大单
    )
    
    # 运行tick级回测
    print("=" * 60)
    print("开始Tick级回测：大单跟随策略")
    print("=" * 60)
    
    result = engine.run_tick(
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 31),  # 回测1个月（tick数据量大）
        stock_code='000001.SZ',
        strategy=strategy
    )
    
    # 输出结果
    print("\n" + result['analysis']['summary'])
    print(f"\n回测耗时: {result['elapsed']:.2f}秒")
    print(f"交易次数: {len(result['trades'])}次")


if __name__ == '__main__':
    main()
