# coding=utf-8
"""
异动预警系统

提供实时监控和预警功能：
1. 涨停板/跌停板监控
2. 大单异动监控
3. 自定义规则配置
4. 多渠道推送（微信/邮件/Webhook）
"""

from .monitor import AlertMonitor
from .rules import AlertRule, RuleManager
from .pusher import Pusher, WeChatPusher, EmailPusher

__all__ = [
    'AlertMonitor',
    'AlertRule',
    'RuleManager',
    'Pusher',
    'WeChatPusher',
    'EmailPusher'
]
