# coding=utf-8
"""
错误处理和重试机制

提供统一的错误处理、重试机制、优雅降级
"""

import time
from functools import wraps
from typing import Callable, Any
from tdx_mcp.utils.log import log


def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 退避因子（每次重试延迟 = delay * backoff ^ retry_count）
    
    Example:
        @retry_on_error(max_retries=3, delay=1.0)
        def unstable_function():
            # 可能失败的函数
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retry_count = 0
            current_delay = delay
            
            while retry_count <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retry_count += 1
                    
                    if retry_count > max_retries:
                        log.error("函数 %s 重试%d次后仍然失败: %s", func.__name__, max_retries, e)
                        raise
                    
                    log.warning(
                        "函数 %s 第%d次失败，%.1f秒后重试: %s", 
                        func.__name__, retry_count, current_delay, e
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        
        return wrapper
    return decorator


def safe_call(func: Callable, default_value: Any = None, *args, **kwargs) -> Any:
    """
    安全调用函数（捕获异常并返回默认值）
    
    Args:
        func: 要调用的函数
        default_value: 失败时返回的默认值
        *args, **kwargs: 传递给func的参数
    
    Returns:
        函数返回值或default_value
    
    Example:
        result = safe_call(client.get_quotes, default_value=[], market=MARKET.SH, code='000001')
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log.warning("安全调用 %s 失败: %s，返回默认值", func.__name__, e)
        return default_value


class GracefulDegradation:
    """
    优雅降级管理器
    
    Example:
        gd = GracefulDegradation()
        
        # 尝试主方案
        data = gd.try_or_fallback(
            primary_func=lambda: client.get_stock_quotes(market, code),
            fallback_func=lambda: {'error': '数据获取失败'},
            error_msg='获取报价失败'
        )
    """
    
    @staticmethod
    def try_or_fallback(
        primary_func: Callable,
        fallback_func: Callable,
        error_msg: str = '操作失败'
    ) -> Any:
        """
        尝试主方案，失败则使用备用方案
        
        Args:
            primary_func: 主方案函数
            fallback_func: 备用方案函数
            error_msg: 错误消息
        
        Returns:
            主方案结果或备用方案结果
        """
        try:
            return primary_func()
        except Exception as e:
            log.warning("%s，使用备用方案: %s", error_msg, e)
            try:
                return fallback_func()
            except Exception as e2:
                log.error("备用方案也失败: %s", e2)
                return {'error': error_msg}


def validate_data(data: Any, required_fields: list = None) -> tuple[bool, str]:
    """
    数据校验函数
    
    Args:
        data: 要校验的数据
        required_fields: 必需字段列表
    
    Returns:
        (is_valid, error_msg)
    
    Example:
        is_valid, error = validate_data(quote, ['close', 'pre_close'])
        if not is_valid:
            return {'error': error}
    """
    if data is None:
        return False, '数据为空'
    
    if isinstance(data, dict) and required_fields:
        for field in required_fields:
            if field not in data:
                return False, f'缺少必需字段: {field}'
    
    return True, ''


def calculate_safely(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法（避免除零错误）
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 默认值（分母为0时返回）
    
    Returns:
        计算结果或默认值
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except Exception:
        return default
