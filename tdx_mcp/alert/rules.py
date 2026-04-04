# coding=utf-8
"""
预警规则配置

支持多种预警类型：
1. 涨停板监控（排除ST、科创、次新等）
2. 跌停板监控
3. 大单异动监控（阈值、时间窗口）
4. 量价异动监控
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import json


@dataclass
class AlertRule:
    """预警规则"""
    
    # 规则基本信息
    rule_id: str
    name: str
    enabled: bool = True
    
    # 预警类型
    alert_type: Literal[
        'limit_up',      # 涨停板
        'limit_down',    # 跌停板
        'large_order',   # 大单异动
        'volume_surge',  # 放量异动
        'price_surge',   # 价格异动
        'turnover_high'  # 高换手率
    ] = 'limit_up'
    
    # 过滤条件
    exclude_st: bool = True           # 排除ST股票
    exclude_new: bool = True          # 排除次新股（上市<60天）
    exclude_kcb: bool = False         # 排除科创板
    min_price: Optional[float] = None  # 最低价格
    max_price: Optional[float] = None  # 最高价格
    min_volume: Optional[int] = None   # 最小成交量
    min_amount: Optional[float] = None # 最小成交额（万元）
    
    # 大单异动参数
    large_order_threshold: float = 500000  # 大单阈值（元）
    large_order_window: int = 5            # 时间窗口（分钟）
    
    # 量价异动参数
    volume_surge_ratio: float = 2.0        # 放量倍数
    price_surge_ratio: float = 3.0         # 价格波动幅度（%）
    turnover_threshold: float = 10.0       # 换手率阈值（%）
    
    # 推送配置
    notify_channels: List[str] = field(default_factory=lambda: ['wechat'])
    notify_frequency: int = 1  # 相同股票推送频率（分钟）
    max_alerts_per_hour: int = 20  # 每小时最大预警数量
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'enabled': self.enabled,
            'alert_type': self.alert_type,
            'exclude_st': self.exclude_st,
            'exclude_new': self.exclude_new,
            'exclude_kcb': self.exclude_kcb,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'min_volume': self.min_volume,
            'min_amount': self.min_amount,
            'large_order_threshold': self.large_order_threshold,
            'large_order_window': self.large_order_window,
            'volume_surge_ratio': self.volume_surge_ratio,
            'price_surge_ratio': self.price_surge_ratio,
            'turnover_threshold': self.turnover_threshold,
            'notify_channels': self.notify_channels,
            'notify_frequency': self.notify_frequency,
            'max_alerts_per_hour': self.max_alerts_per_hour,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlertRule':
        """从字典创建"""
        # 处理日期字段
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


class RuleManager:
    """规则管理器"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self._load_default_rules()
    
    def _load_default_rules(self):
        """加载默认规则"""
        default_rules = [
            AlertRule(
                rule_id='limit_up_monitor',
                name='涨停板监控',
                alert_type='limit_up',
                exclude_st=True,
                exclude_new=True,
                min_volume=100000,
                notify_channels=['wechat']
            ),
            AlertRule(
                rule_id='limit_down_monitor',
                name='跌停板监控',
                alert_type='limit_down',
                exclude_st=False,
                notify_channels=['wechat', 'sms']
            ),
            AlertRule(
                rule_id='large_order_monitor',
                name='大单异动监控',
                alert_type='large_order',
                large_order_threshold=500000,
                large_order_window=5,
                notify_channels=['wechat']
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
    
    def add_rule(self, rule: AlertRule):
        """添加规则"""
        self.rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str):
        """移除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """获取规则"""
        return self.rules.get(rule_id)
    
    def get_enabled_rules(self) -> List[AlertRule]:
        """获取所有启用的规则"""
        return [rule for rule in self.rules.values() if rule.enabled]
    
    def get_rules_by_type(self, alert_type: str) -> List[AlertRule]:
        """按类型获取规则"""
        return [
            rule for rule in self.rules.values()
            if rule.enabled and rule.alert_type == alert_type
        ]
    
    def save_to_file(self, filepath: str):
        """保存到文件"""
        data = {
            rule_id: rule.to_dict()
            for rule_id, rule in self.rules.items()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """从文件加载"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.rules = {
                rule_id: AlertRule.from_dict(rule_data)
                for rule_id, rule_data in data.items()
            }
        except FileNotFoundError:
            # 文件不存在，使用默认规则
            pass
        except Exception as e:
            # 加载失败，使用默认规则
            print(f"加载规则文件失败: {e}")
            self._load_default_rules()
