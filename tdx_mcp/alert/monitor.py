# coding=utf-8
"""
异动监控引擎

核心功能：
1. 实时监控市场异动
2. 应用用户配置的规则
3. 生成预警消息
4. 调用推送系统
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import time
import threading

from .rules import AlertRule, RuleManager
from .pusher import PusherManager, AlertMessage


@dataclass
class StockSnapshot:
    """股票快照"""
    code: str
    name: str
    market: str
    price: float
    pre_close: float
    change_pct: float
    volume: int
    amount: float
    turnover: float
    high: float
    low: float
    open: float
    timestamp: datetime
    
    # 判断是否涨停/跌停
    @property
    def is_limit_up(self) -> bool:
        """是否涨停"""
        return self.change_pct >= 9.9  # ST股5%，普通股10%，科创/创业20%
    
    @property
    def is_limit_down(self) -> bool:
        """是否跌停"""
        return self.change_pct <= -9.9


@dataclass
class Alert:
    """预警记录"""
    stock_code: str
    stock_name: str
    alert_type: str
    message: str
    timestamp: datetime
    rule_id: str
    pushed: bool = False
    push_channels: List[str] = None
    
    def __post_init__(self):
        if self.push_channels is None:
            self.push_channels = []


class AlertMonitor:
    """异动监控引擎"""
    
    def __init__(
        self,
        client,
        rule_manager: RuleManager = None,
        pusher_manager: PusherManager = None
    ):
        """
        Args:
            client: QuotationClient实例
            rule_manager: 规则管理器
            pusher_manager: 推送器管理器
        """
        self.client = client
        self.rule_manager = rule_manager or RuleManager()
        self.pusher_manager = pusher_manager or PusherManager()
        
        # 监控状态
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # 历史记录（防重复推送）
        self._alert_history: Dict[str, datetime] = {}
        self._alert_lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            'total_checks': 0,
            'total_alerts': 0,
            'push_success': 0,
            'push_failed': 0
        }
    
    def check_stocks(self, stocks: List[StockSnapshot]) -> List[Alert]:
        """
        检查股票列表并生成预警
        
        Args:
            stocks: 股票快照列表
        
        Returns:
            List[Alert]: 预警列表
        """
        alerts = []
        rules = self.rule_manager.get_enabled_rules()
        
        for stock in stocks:
            for rule in rules:
                # 检查是否符合规则
                alert = self._check_rule(stock, rule)
                if alert:
                    alerts.append(alert)
        
        self.stats['total_checks'] += 1
        return alerts
    
    def _check_rule(self, stock: StockSnapshot, rule: AlertRule) -> Optional[Alert]:
        """检查单个规则"""
        
        # 1. 过滤条件检查
        if not self._apply_filters(stock, rule):
            return None
        
        # 2. 根据预警类型检查
        alert_message = None
        
        if rule.alert_type == 'limit_up':
            if stock.is_limit_up:
                alert_message = f"涨停板！当前价{stock.price:.2f}，涨幅{stock.change_pct:.2f}%，成交额{stock.amount/10000:.0f}万"
        
        elif rule.alert_type == 'limit_down':
            if stock.is_limit_down:
                alert_message = f"跌停板！当前价{stock.price:.2f}，跌幅{stock.change_pct:.2f}%"
        
        elif rule.alert_type == 'large_order':
            # 大单异动需要逐笔数据，这里简化处理
            # 实际应该调用get_transaction接口
            pass
        
        elif rule.alert_type == 'volume_surge':
            # 放量异动（需要历史数据对比）
            pass
        
        elif rule.alert_type == 'turnover_high':
            if stock.turnover >= rule.turnover_threshold:
                alert_message = f"高换手率！换手率{stock.turnover:.2f}%，超过阈值{rule.turnover_threshold}%"
        
        # 3. 生成预警
        if alert_message:
            return Alert(
                stock_code=stock.code,
                stock_name=stock.name,
                alert_type=rule.alert_type,
                message=alert_message,
                timestamp=datetime.now(),
                rule_id=rule.rule_id,
                push_channels=rule.notify_channels
            )
        
        return None
    
    def _apply_filters(self, stock: StockSnapshot, rule: AlertRule) -> bool:
        """应用过滤条件"""
        
        # 排除ST
        if rule.exclude_st and 'ST' in stock.name:
            return False
        
        # 排除科创板（688开头）
        if rule.exclude_kcb and stock.code.startswith('688'):
            return False
        
        # 价格区间
        if rule.min_price and stock.price < rule.min_price:
            return False
        if rule.max_price and stock.price > rule.max_price:
            return False
        
        # 最小成交量
        if rule.min_volume and stock.volume < rule.min_volume:
            return False
        
        # 最小成交额
        if rule.min_amount and stock.amount < rule.min_amount * 10000:
            return False
        
        return True
    
    def push_alert(self, alert: Alert) -> bool:
        """推送预警"""
        
        # 检查是否重复推送
        with self._alert_lock:
            alert_key = f"{alert.stock_code}_{alert.alert_type}"
            last_time = self._alert_history.get(alert_key)
            
            # 获取规则的推送频率
            rule = self.rule_manager.get_rule(alert.rule_id)
            if rule and last_time:
                freq_minutes = rule.notify_frequency
                if datetime.now() - last_time < timedelta(minutes=freq_minutes):
                    # 未到推送频率，跳过
                    return False
            
            # 更新推送历史
            self._alert_history[alert_key] = datetime.now()
        
        # 生成推送消息
        message = AlertMessage(
            title=self._get_alert_title(alert),
            content=alert.message,
            stock_code=alert.stock_code,
            stock_name=alert.stock_name,
            alert_type=alert.alert_type,
            timestamp=alert.timestamp
        )
        
        # 推送到指定渠道
        results = self.pusher_manager.push_to_channels(
            message,
            alert.push_channels
        )
        
        # 更新统计
        self.stats['total_alerts'] += 1
        if any(results.values()):
            self.stats['push_success'] += 1
            alert.pushed = True
        else:
            self.stats['push_failed'] += 1
        
        return alert.pushed
    
    def _get_alert_title(self, alert: Alert) -> str:
        """生成预警标题"""
        type_names = {
            'limit_up': '涨停板',
            'limit_down': '跌停板',
            'large_order': '大单异动',
            'volume_surge': '放量异动',
            'price_surge': '价格异动',
            'turnover_high': '高换手率'
        }
        
        type_name = type_names.get(alert.alert_type, '异动')
        return f"【{type_name}】{alert.stock_name} ({alert.stock_code})"
    
    def start_monitoring(self, interval: int = 30):
        """
        启动后台监控
        
        Args:
            interval: 检查间隔（秒）
        """
        if self._running:
            return
        
        self._running = True
        
        def _monitor_loop():
            while self._running:
                try:
                    # 获取实时数据
                    stocks = self._fetch_realtime_stocks()
                    
                    # 检查异动
                    alerts = self.check_stocks(stocks)
                    
                    # 推送预警
                    for alert in alerts:
                        self.push_alert(alert)
                    
                    # 清理过期历史
                    self._cleanup_history()
                    
                except Exception as e:
                    print(f"监控异常: {e}")
                
                time.sleep(interval)
        
        self._monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _fetch_realtime_stocks(self) -> List[StockSnapshot]:
        """获取实时股票数据（简化版）"""
        # 这里应该调用client的接口获取全市场数据
        # 简化实现，返回空列表
        # 实际应该调用：
        # - get_stock_quotes_list 获取股票列表
        # - 转换为StockSnapshot对象
        return []
    
    def _cleanup_history(self):
        """清理过期的推送历史"""
        with self._alert_lock:
            expire_time = datetime.now() - timedelta(hours=24)
            keys_to_remove = [
                k for k, v in self._alert_history.items()
                if v < expire_time
            ]
            for k in keys_to_remove:
                del self._alert_history[k]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'running': self._running,
            'alert_history_size': len(self._alert_history),
            'active_rules': len(self.rule_manager.get_enabled_rules()),
            'active_pushers': len(self.pusher_manager.pushers)
        }
