# coding=utf-8
"""
回测引擎核心

提供完整的回测流程控制
"""

from typing import Dict, List, Optional, Type
from datetime import datetime, date, timedelta
import time

from .strategy import BaseStrategy
from .context import ContextInfo
from .matcher import OrderMatcher, TickMatcher
from .analyzer import PerformanceAnalyzer
from tdx_mcp.client.quotationClient import QuotationClient
from tdx_mcp.const import MARKET
from tdx_mcp.utils.log import log


class BacktestEngine:
    """
    回测引擎
    
    功能：
    - 数据加载
    - 事件驱动
    - 策略调度
    - 讒合处理
    - 绩效分析
    """
    
    def __init__(self, 
                 initial_capital: float = 1000000.0,
                 commission_rate: float = 0.0,
                 stamp_duty_rate: float = 1.0,
                 slippage_rate: float = 1.0):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            commission_rate: 佣金率（万分之几）
            stamp_duty_rate: 印花税率（千分之几）
            slippage_rate: 滑点率（千分之几）
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.stamp_duty_rate = stamp_duty_rate
        self.slippage_rate = slippage_rate
        
        # 数据客户端
        self.client = None
        
        # 策略
        self.strategy = None
        self.context = None
        
        # 订单撮合引擎
        self.matcher = OrderMatcher(
            commission_rate=0.0001 * commission_rate,  # 转换为小数
            stamp_duty_rate=0.001 * stamp_duty_rate,
            slippage_rate=0.001 * slippage_rate
        )
        self.tick_matcher = TickMatcher(
            commission_rate=0.0001 * commission_rate,
            stamp_duty_rate=0.001 * stamp_duty_rate,
            slippage_rate=0.001 * slippage_rate
        )
        
        # 数据缓存
        self._kline_cache = {}
        self._tick_cache = {}
        self._current_prices = {}
        
        # 回测日期范围
        self.start_date = None
        self.end_date = None
        self.current_date = None
        
        # 绩效分析器
        self.analyzer = None
    
    def set_strategy(self, strategy: BaseStrategy):
        """
        设置策略
        
        Args:
            strategy: 策略实例
        """
        self.strategy = strategy
    
    def run(self, 
           start_date: date, 
           end_date: date,
           strategy: Optional[BaseStrategy] = None) -> Dict:
        """
        运行回测
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            strategy: 策略实例（可选，如未设置需先调用set_strategy）
        
        Returns:
            Dict: 回测结果
        """
        if strategy:
            self.set_strategy(strategy)
        
        if not self.strategy:
            raise ValueError("未设置策略")
        
        # 初始化
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = start_date
        
        # 初始化客户端
        self.client = QuotationClient(True, True)
        self.client.connect().login()
        
        # 初始化上下文
        self.context = ContextInfo(self, start_date, end_date)
        
        # 初始化策略
        log.info("初始化策略: %s", self.strategy.name)
        self.strategy.init(self.context)
        
        # 加载数据
        log.info("加载历史数据...")
        self._load_data()
        
        # 运行回测
        log.info("开始回测: %s 至 %s", start_date, end_date)
        start_time = time.time()
        
        # 逐日回测
        current = start_date
        while current <= end_date:
            self.current_date = current
            self.context.current_date = current
            
            # 获取当日K线数据
            bars = self._get_bars_for_date(current)
            
            if bars:
                # 触发handle_bar事件
                for bar in bars:
                    self.strategy.handle_bar(self.context, bar)
            
            # 记录每日净值
            self._record_daily_value(current)
            
            # 移动到下一天
            current += timedelta(days=1)
        
        # 回测结束
        elapsed = time.time() - start_time
        log.info("回测完成，耗时: %.2f秒", elapsed)
        
        # 绩效分析
        self.analyzer = PerformanceAnalyzer(self.context.portfolio)
        analysis = self.analyzer.analyze()
        
        # 断开连接
        self.client.disconnect()
        
        return {
            'elapsed': elapsed,
            'analysis': analysis,
            'trades': self.context.portfolio.trades,
            'daily_values': self.context.portfolio.daily_values
        }
    
    def run_tick(self, 
                 start_date: date, 
                 end_date: date,
                 stock_code: str,
                 strategy: Optional[BaseStrategy] = None) -> Dict:
        """
        运行tick级回测
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            stock_code: 股票代码
            strategy: 策略实例
        
        Returns:
            Dict: 回测结果
        """
        if strategy:
            self.set_strategy(strategy)
        
        if not self.strategy:
            raise ValueError("未设置策略")
        
        # 初始化
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = start_date
        
        # 初始化客户端
        self.client = QuotationClient(True, True)
        self.client.connect().login()
        
        # 初始化上下文
        self.context = ContextInfo(self, start_date, end_date)
        
        # 初始化策略
        log.info("初始化策略: %s", self.strategy.name)
        self.strategy.init(self.context)
        
        # 加载tick数据
        log.info("加载tick数据: %s", stock_code)
        self._load_tick_data(stock_code)
        
        # 运行tick级回测
        log.info("开始tick级回测: %s 至 %s", start_date, end_date)
        start_time = time.time()
        
        # 逐日回测
        current = start_date
        while current <= end_date:
            self.current_date = current
            self.context.current_date = current
            
            # 获取当日tick数据
            ticks = self._get_ticks_for_date(current, stock_code)
            
            if ticks:
                # 逐tick触发
                for tick in ticks:
                    # 更新当前价格
                    self._current_prices[stock_code] = tick['price']
                    
                    # 触发handle_tick事件
                    self.strategy.handle_tick(self.context, tick)
            
            # 记录每日净值
            self._record_daily_value(current)
            
            # 移动到下一天
            current += timedelta(days=1)
        
        # 回测结束
        elapsed = time.time() - start_time
        log.info("tick级回测完成，耗时: %.2f秒", elapsed)
        
        # 绩效分析
        self.analyzer = PerformanceAnalyzer(self.context.portfolio)
        analysis = self.analyzer.analyze()
        
        # 断开连接
        self.client.disconnect()
        
        return {
            'elapsed': elapsed,
            'analysis': analysis,
            'trades': self.context.portfolio.trades,
            'daily_values': self.context.portfolio.daily_values
        }
    
    # ==================== 数据加载 ====================
    
    def _load_data(self):
        """加载历史K线数据"""
        # 子类实现
        pass
    
    def _load_tick_data(self, stock_code: str):
        """加载tick数据"""
        # 子类实现
        pass
    
    def _get_bars_for_date(self, date: date) -> List[Dict]:
        """
        获取指定日期的K线数据
        
        Args:
            date: 日期
        
        Returns:
            List[Dict]: K线数据列表
        """
        # 子类实现
        return []
    
    def _get_ticks_for_date(self, date: date, stock_code: str) -> List[Dict]:
        """
        获取指定日期的tick数据
        
        Args:
            date: 日期
            stock_code: 股票代码
        
        Returns:
            List[Dict]: tick数据列表
        """
        # 子类实现
        return []
    
    # ==================== 订单处理 ====================
    
    def place_order(self, 
                   stock_code: str,
                   direction: str,
                   quantity: int,
                   price_type: str = 'MARKET',
                   limit_price: Optional[float] = None,
                   context: Optional[ContextInfo] = None):
        """
        下单
        
        Args:
            stock_code: 股票代码
            direction: 方向（'BUY'/'SELL'）
            quantity: 数量
            price_type: 价格类型（'MARKET'/'LIMIT'）
            limit_price: 限价（限价单必须）
            context: 上下文（可选）
        """
        order = {
            'stock_code': stock_code,
            'direction': direction,
            'quantity': quantity,
            'price_type': price_type,
            'limit_price': limit_price,
            'date': self.current_date
        }
        
        # 获取当前价格
        current_price = self._current_prices.get(stock_code, 0.0)
        
        # 撮合订单
        result = self.matcher.match_order(order, current_price)
        
        if result['success']:
            # 执行交易
            self._execute_trade(order, result)
            
            # 回调通知策略
            if context and hasattr(self.strategy, 'on_order_filled'):
                self.strategy.on_order_filled(context, {**order, **result})
    
    def _execute_trade(self, order: Dict, match_result: Dict):
        """
        执行交易
        
        Args:
            order: 订单信息
            match_result: 撮合结果
        """
        # 记录交易
        trade = {
            'stock_code': order['stock_code'],
            'direction': order['direction'],
            'quantity': match_result['executed_quantity'],
            'price': match_result['executed_price'],
            'total_cost': match_result['total_cost'],
            'commission': match_result['commission'],
            'stamp_duty': match_result['stamp_duty'],
            'transfer_fee': match_result['transfer_fee'],
            'date': order['date']
        }
        
        # 更新持仓
        if order['direction'] == 'BUY':
            self.context.portfolio.buy(
                order['stock_code'],
                match_result['executed_quantity'],
                match_result['executed_price'],
                order['date']
            )
        else:
            self.context.portfolio.sell(
                order['stock_code'],
                match_result['executed_quantity'],
                match_result['executed_price'],
                order['date']
            )
        
        self.context.portfolio.trades.append(trade)
    
    # ==================== 辅助方法 ====================
    
    def get_history_data(self, stock_code: str, field: str, length: int, date: date) -> List:
        """
        获取历史数据（ContextInfo调用）
        
        Args:
            stock_code: 股票代码
            field: 字段名
            length: 数据长度
            date: 截止日期
        
        Returns:
            List: 历史数据
        """
        # 子类实现
        return []
    
    def get_current_data(self, stock_code: str, field: str, date: date):
        """
        获取当前数据（ContextInfo调用）
        
        Args:
            stock_code: 股票代码
            field: 字段名
            date: 日期
        
        Returns:
            当前值
        """
        # 子类实现
        return 0
    
    def get_tick_data(self, stock_code: str, date: date) -> List[Dict]:
        """
        获取tick数据（ContextInfo调用）
        
        Args:
            stock_code: 股票代码
            date: 日期
        
        Returns:
            List[Dict]: tick数据列表
        """
        # 子类实现
        return []
    
    def get_current_prices(self) -> Dict[str, float]:
        """
        获取当前价格字典
        
        Returns:
            Dict: {股票代码: 当前价格}
        """
        return self._current_prices
    
    def _record_daily_value(self, date: date):
        """
        记录每日净值
        
        Args:
            date: 日期
        """
        self.context.portfolio.record_daily_value(date, self._current_prices)


# 示例：如何使用回测引擎
if __name__ == '__main__':
    from .strategy import SimpleStrategy
    from datetime import date
    
    # 创建引擎
    engine = BacktestEngine(
        initial_capital=1000000.0,
        commission_rate=0.3,  # 0.03%
        stamp_duty_rate=1.0,  # 0.1%
        slippage_rate=0.1   # 0.01%
    )
    
    # 创建策略
    strategy = SimpleStrategy(
        stock_code='000001.SZ',
        fast_period=5,
        slow_period=20
    )
    
    # 运行回测
    result = engine.run(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        strategy=strategy
    )
    
    # 输出结果
    print(result['analysis']['summary'])
