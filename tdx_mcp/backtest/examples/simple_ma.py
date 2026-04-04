#!/usr/bin/env python3
# coding=utf-8
"""
简单均线策略示例

演示如何使用回测框架
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import date
from tdx_mcp.backtest.strategy import BaseStrategy
from tdx_mcp.backtest.engine import BacktestEngine


class SimpleMAStrategy(BaseStrategy):
    """
    简单双均线策略
    
    策略逻辑：
    - 快速均线上穿慢速均线 → 买入
    - 快速均线下穿慢速均线 → 卖出
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
        context.position_flag = False  # 是否持仓
        
        context.log(f"初始化策略: {self.stock_code}, 快线{self.fast_period}日, 慢线{self.slow_period}日")
    
    def handle_bar(self, context, bar):
        """处理K线事件"""
        # 获取历史收盘价
        closes = context.history('close', self.slow_period)
        
        if len(closes) < self.slow_period:
            return
        
        # 计算均线
        fast_ma = sum(closes[-self.fast_period:]) / self.fast_period
        slow_ma = sum(closes[-self.slow_period:]) / self.slow_period
        
        # 获取当前持仓
        current_pos = context.position(self.stock_code)
        
        # 交易逻辑
        if fast_ma > slow_ma and current_pos == 0:
            # 金叉买入（满仓）
            context.order_target_percent(self.stock_code, 1.0)
            context.log(f"金叉买入: 快线{fast_ma:.2f} > 慢线{slow_ma:.2f}")
        elif fast_ma < slow_ma and current_pos > 0:
            # 死叉卖出（清仓）
            context.order_target(self.stock_code, 0)
            context.log(f"死叉卖出: 快线{fast_ma:.2f} < 慢线{slow_ma:.2f}")


def main():
    """运行回测"""
    # 创建引擎
    engine = BacktestEngine(
        initial_capital=1000000.0,
        commission_rate=0.3,  # 万三佣金
        stamp_duty_rate=1.0,  # 千一印花税
        slippage_rate=0.5     # 千0.5滑点
    )
    
    # 创建策略
    strategy = SimpleMAStrategy(
        stock_code='000001.SZ',
        fast_period=5,
        slow_period=20
    )
    
    # 运行回测
    print("=" * 60)
    print("开始回测：简单双均线策略")
    print("=" * 60)
    
    result = engine.run(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        strategy=strategy
    )
    
    # 输出结果
    print("\n" + result['analysis']['summary'])
    print("\n详细报告已生成")
    
    # 生成报告
    analyzer = engine.analyzer
    report = analyzer.generate_report('backtest_report.txt')
    print(report)


if __name__ == '__main__':
    main()
