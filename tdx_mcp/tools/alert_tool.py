# coding=utf-8
"""
异动预警MCP工具

提供MCP接口：
1. 配置预警规则
2. 启动/停止监控
3. 查看预警历史
4. 测试推送
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from ..client.quotationClient import QuotationClient
from ..alert import AlertMonitor, AlertRule, RuleManager
from ..alert.pusher import WeChatPusher, EmailPusher, WebhookPusher, PusherManager


# 全局实例（按用户会话隔离）
_monitors: Dict[str, AlertMonitor] = {}
_clients: Dict[str, QuotationClient] = {}


def get_client(session_id: str = 'default') -> QuotationClient:
    """获取或创建客户端"""
    if session_id not in _clients:
        _clients[session_id] = QuotationClient(True, True)
        _clients[session_id].connect().login()
    return _clients[session_id]


def get_monitor(session_id: str = 'default') -> AlertMonitor:
    """获取或创建监控器"""
    if session_id not in _monitors:
        client = get_client(session_id)
        _monitors[session_id] = AlertMonitor(client)
    return _monitors[session_id]


# ========== MCP工具函数 ==========

def alert_config_rule(
    rule_id: str,
    alert_type: str,
    enabled: bool = True,
    exclude_st: bool = True,
    min_volume: int = None,
    notify_channels: List[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    配置预警规则
    
    Args:
        rule_id: 规则ID
        alert_type: 预警类型（limit_up/limit_down/large_order/turnover_high）
        enabled: 是否启用
        exclude_st: 是否排除ST股票
        min_volume: 最小成交量
        notify_channels: 推送渠道列表
    
    Returns:
        Dict: 配置结果
    """
    try:
        monitor = get_monitor()
        
        # 创建或更新规则
        rule = AlertRule(
            rule_id=rule_id,
            name=f"{alert_type}_rule",
            alert_type=alert_type,
            enabled=enabled,
            exclude_st=exclude_st,
            min_volume=min_volume,
            notify_channels=notify_channels or ['wechat'],
            **kwargs
        )
        
        monitor.rule_manager.add_rule(rule)
        
        return {
            'success': True,
            'rule_id': rule_id,
            'message': f'规则{rule_id}配置成功'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def alert_start_monitoring(
    interval: int = 30,
    session_id: str = 'default'
) -> Dict[str, Any]:
    """
    启动异动监控
    
    Args:
        interval: 检查间隔（秒）
        session_id: 会话ID
    
    Returns:
        Dict: 启动结果
    """
    try:
        monitor = get_monitor(session_id)
        monitor.start_monitoring(interval)
        
        return {
            'success': True,
            'message': '异动监控已启动',
            'interval': interval,
            'stats': monitor.get_stats()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def alert_stop_monitoring(session_id: str = 'default') -> Dict[str, Any]:
    """
    停止异动监控
    
    Args:
        session_id: 会话ID
    
    Returns:
        Dict: 停止结果
    """
    try:
        monitor = get_monitor(session_id)
        monitor.stop_monitoring()
        
        return {
            'success': True,
            'message': '异动监控已停止',
            'final_stats': monitor.get_stats()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def alert_get_stats(session_id: str = 'default') -> Dict[str, Any]:
    """
    获取监控统计信息
    
    Args:
        session_id: 会话ID
    
    Returns:
        Dict: 统计信息
    """
    try:
        monitor = get_monitor(session_id)
        return {
            'success': True,
            'stats': monitor.get_stats()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def alert_list_rules() -> Dict[str, Any]:
    """
    列出所有预警规则
    
    Returns:
        Dict: 规则列表
    """
    try:
        monitor = get_monitor()
        rules = monitor.rule_manager.rules
        
        return {
            'success': True,
            'rules': {
                rule_id: rule.to_dict()
                for rule_id, rule in rules.items()
            },
            'count': len(rules)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def alert_setup_wechat_pusher(
    send_key: str,
    session_id: str = 'default'
) -> Dict[str, Any]:
    """
    配置微信推送器
    
    Args:
        send_key: Server酱的SendKey
        session_id: 会话ID
    
    Returns:
        Dict: 配置结果
    """
    try:
        monitor = get_monitor(session_id)
        pusher = WeChatPusher(send_key)
        
        # 测试连接
        if not pusher.test_connection():
            return {
                'success': False,
                'error': '微信推送器连接测试失败'
            }
        
        monitor.pusher_manager.add_pusher('wechat', pusher)
        
        return {
            'success': True,
            'message': '微信推送器配置成功'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def alert_test_push(
    stock_code: str = '000001',
    stock_name: str = '测试股票',
    session_id: str = 'default'
) -> Dict[str, Any]:
    """
    测试推送功能
    
    Args:
        stock_code: 股票代码
        stock_name: 股票名称
        session_id: 会话ID
    
    Returns:
        Dict: 测试结果
    """
    try:
        from ..alert.pusher import AlertMessage
        
        monitor = get_monitor(session_id)
        
        message = AlertMessage(
            title=f"【测试预警】{stock_name} ({stock_code})",
            content="这是一条测试预警消息",
            stock_code=stock_code,
            stock_name=stock_name,
            alert_type='test',
            timestamp=datetime.now()
        )
        
        results = monitor.pusher_manager.push_to_all(message)
        
        return {
            'success': True,
            'push_results': results,
            'message': '测试推送完成'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def alert_realtime_check(
    market: int = 6,
    session_id: str = 'default'
) -> Dict[str, Any]:
    """
    实时检查异动（单次）
    
    Args:
        market: 市场类型（6=A股）
        session_id: 会话ID
    
    Returns:
        Dict: 检查结果
    """
    try:
        from ..alert.monitor import StockSnapshot
        from ..const import CATEGORY
        
        monitor = get_monitor(session_id)
        client = get_client(session_id)
        
        # 获取股票列表
        stocks_data = client.get_stock_quotes_list(
            CATEGORY(market),
            start=0,
            count=100  # 限制数量，避免超时
        )
        
        # 转换为快照
        snapshots = []
        for s in stocks_data:
            try:
                snapshot = StockSnapshot(
                    code=s.get('code', ''),
                    name=s.get('name', ''),
                    market='SH' if market == 0 else 'SZ',
                    price=float(s.get('close', 0)),
                    pre_close=float(s.get('pre_close', 0)),
                    change_pct=0.0,  # 需要计算
                    volume=int(s.get('vol', 0)),
                    amount=float(s.get('amount', 0)),
                    turnover=0.0,  # 需要解析
                    high=float(s.get('high', 0)),
                    low=float(s.get('low', 0)),
                    open=float(s.get('open', 0)),
                    timestamp=datetime.now()
                )
                
                # 计算涨幅
                if snapshot.pre_close > 0:
                    snapshot.change_pct = (
                        (snapshot.price - snapshot.pre_close) / snapshot.pre_close * 100
                    )
                
                snapshots.append(snapshot)
            except Exception as e:
                continue
        
        # 检查异动
        alerts = monitor.check_stocks(snapshots)
        
        # 推送预警
        pushed_count = 0
        for alert in alerts:
            if monitor.push_alert(alert):
                pushed_count += 1
        
        return {
            'success': True,
            'stocks_checked': len(snapshots),
            'alerts_found': len(alerts),
            'alerts_pushed': pushed_count,
            'alerts': [
                {
                    'stock_code': a.stock_code,
                    'stock_name': a.stock_name,
                    'alert_type': a.alert_type,
                    'message': a.message,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in alerts[:10]  # 只返回前10条
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
