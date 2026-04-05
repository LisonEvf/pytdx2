# coding=utf-8
"""
板块联动分析工具
功能：
1. 板块涨跌统计
2. 板块资金流向
3. 领涨/领跌股票识别
4. 板块轮动信号检测
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..tdxClient import QuotationClient
from ..const import MARKET, CATEGORY, BLOCK_FILE_TYPE


def safe_call(func):
    """安全调用装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {'error': str(e), 'function': func.__name__}
    return wrapper


@safe_call
def sector_overview(
    client: QuotationClient,
    sector_type: str = 'industry'  # industry/concept/region
) -> Dict[str, Any]:
    """
    板块概览
    
    Args:
        client: 通达信客户端
        sector_type: 板块类型（industry行业/concept概念/region地区）
    
    Returns:
        {
            'sector_type': 'industry',
            'sectors': [
                {
                    'name': '软件开发',
                    'code': 'BK0428',
                    'change_pct': 2.5,
                    'turnover_rate': 3.2,
                    'amount': 1500000000,
                    'leading_stock': {'code': '000001', 'name': '平安银行', 'change_pct': 5.2},
                    'stocks_count': 50
                }
            ]
        }
    """
    # 获取板块分类
    block_type_map = {
        'industry': BLOCK_FILE_TYPE.INDUSTRY,
        'concept': BLOCK_FILE_TYPE.CONCEPT,
        'region': BLOCK_FILE_TYPE.REGION
    }
    
    block_type = block_type_map.get(sector_type, BLOCK_FILE_TYPE.INDUSTRY)
    
    # 获取板块列表
    sectors_data = client.get_block_info(block_type)
    
    if not sectors_data:
        return {'error': '无法获取板块数据', 'sector_type': sector_type}
    
    sectors_list = []
    
    for sector in sectors_data[:50]:  # 只取前50个板块
        sector_code = sector.get('code', '')
        sector_name = sector.get('name', '')
        
        # 获取板块成分股行情
        try:
            stocks = client.get_block_stock_quotes(sector_code, block_type)
            
            if not stocks:
                continue
            
            # 计算板块涨跌幅
            total_change = 0
            total_amount = 0
            total_turnover = 0
            valid_stocks = 0
            
            leading_stock = None
            max_change = -100
            
            for stock in stocks:
                change_pct = stock.get('change_pct', 0)
                amount = stock.get('amount', 0)
                turnover_rate = stock.get('turnover_rate', 0)
                
                if change_pct is not None and not np.isnan(change_pct):
                    total_change += change_pct
                    valid_stocks += 1
                    
                    # 找领涨股
                    if change_pct > max_change:
                        max_change = change_pct
                        leading_stock = {
                            'code': stock.get('code', ''),
                            'name': stock.get('name', ''),
                            'change_pct': change_pct
                        }
                
                if amount:
                    total_amount += amount
                if turnover_rate:
                    total_turnover += turnover_rate
            
            if valid_stocks > 0:
                avg_change = total_change / valid_stocks
                avg_turnover = total_turnover / valid_stocks
                
                sectors_list.append({
                    'name': sector_name,
                    'code': sector_code,
                    'change_pct': round(avg_change, 2),
                    'turnover_rate': round(avg_turnover, 2),
                    'amount': total_amount,
                    'leading_stock': leading_stock,
                    'stocks_count': len(stocks)
                })
        
        except Exception as e:
            continue
    
    # 按涨跌幅排序
    sectors_list.sort(key=lambda x: x['change_pct'], reverse=True)
    
    return {
        'sector_type': sector_type,
        'sectors': sectors_list,
        'count': len(sectors_list),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


@safe_call
def sector_capital_flow(
    client: QuotationClient,
    sector_code: str,
    days: int = 5
) -> Dict[str, Any]:
    """
    板块资金流向分析
    
    Args:
        client: 通达信客户端
        sector_code: 板块代码
        days: 分析天数
    
    Returns:
        {
            'sector_code': 'BK0428',
            'sector_name': '软件开发',
            'days': 5,
            'total_inflow': 5000000000,
            'total_outflow': 3000000000,
            'net_inflow': 2000000000,
            'daily_flow': [...],
            'hot_stocks': [...]
        }
    """
    # 获取板块成分股
    stocks = client.get_block_stock_quotes(sector_code, BLOCK_FILE_TYPE.INDUSTRY)
    
    if not stocks:
        return {'error': '无法获取板块成分股', 'sector_code': sector_code}
    
    # 计算板块资金流向
    total_inflow = 0
    total_outflow = 0
    
    hot_stocks = []
    
    for stock in stocks:
        code = stock.get('code', '')
        name = stock.get('name', '')
        
        # 获取个股资金流向（最近N天）
        try:
            # 这里简化处理，使用当日成交额估算
            amount = stock.get('amount', 0)
            change_pct = stock.get('change_pct', 0)
            
            if amount and change_pct:
                # 上涨算流入，下跌算流出
                if change_pct > 0:
                    inflow = amount * (change_pct / 100) * 0.5  # 估算
                    total_inflow += inflow
                else:
                    outflow = abs(amount * (change_pct / 100) * 0.5)
                    total_outflow += outflow
                
                # 记录活跃股票
                if amount > 100000000:  # 成交额>1亿
                    hot_stocks.append({
                        'code': code,
                        'name': name,
                        'amount': amount,
                        'change_pct': change_pct
                    })
        
        except Exception:
            continue
    
    # 按成交额排序
    hot_stocks.sort(key=lambda x: x['amount'], reverse=True)
    
    return {
        'sector_code': sector_code,
        'sector_name': stocks[0].get('sector_name', '未知板块') if stocks else '未知板块',
        'days': days,
        'total_inflow': total_inflow,
        'total_outflow': total_outflow,
        'net_inflow': total_inflow - total_outflow,
        'hot_stocks': hot_stocks[:10],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


@safe_call
def sector_rotation_signal(
    client: QuotationClient,
    lookback_days: int = 5
) -> Dict[str, Any]:
    """
    板块轮动信号检测
    
    Args:
        client: 通达信客户端
        lookback_days: 回看天数
    
    Returns:
        {
            'signals': [
                {
                    'type': '强势启动',
                    'sector': '人工智能',
                    'strength': 0.8,
                    'description': '连续3天上涨，成交放大'
                }
            ],
            'recommendation': '关注AI板块'
        }
    """
    # 获取行业板块数据
    sectors_data = client.get_block_info(BLOCK_FILE_TYPE.INDUSTRY)
    
    if not sectors_data:
        return {'error': '无法获取板块数据'}
    
    signals = []
    
    for sector in sectors_data[:30]:  # 分析前30个板块
        sector_code = sector.get('code', '')
        sector_name = sector.get('name', '')
        
        try:
            stocks = client.get_block_stock_quotes(sector_code, BLOCK_FILE_TYPE.INDUSTRY)
            
            if not stocks or len(stocks) < 5:
                continue
            
            # 计算板块强度
            up_count = 0
            down_count = 0
            total_amount = 0
            
            for stock in stocks:
                change_pct = stock.get('change_pct', 0)
                amount = stock.get('amount', 0)
                
                if change_pct > 0:
                    up_count += 1
                elif change_pct < 0:
                    down_count += 1
                
                if amount:
                    total_amount += amount
            
            total_stocks = len(stocks)
            up_ratio = up_count / total_stocks if total_stocks > 0 else 0
            
            # 判断信号
            signal_type = None
            strength = 0
            description = ''
            
            # 强势启动信号
            if up_ratio >= 0.8 and total_amount > 5000000000:
                signal_type = '强势启动'
                strength = min(up_ratio + 0.1, 1.0)
                description = f'上涨股票{int(up_ratio*100)}%，成交额{total_amount/100000000:.1f}亿'
            
            # 超跌反弹信号
            elif up_ratio <= 0.2 and total_amount > 3000000000:
                signal_type = '超跌反弹'
                strength = 0.6
                description = f'下跌股票{int((1-up_ratio)*100)}%，可能有反弹'
            
            # 分化信号
            elif 0.4 <= up_ratio <= 0.6 and total_amount > 2000000000:
                signal_type = '板块分化'
                strength = 0.5
                description = '多空分歧，关注龙头'
            
            if signal_type:
                signals.append({
                    'type': signal_type,
                    'sector': sector_name,
                    'sector_code': sector_code,
                    'strength': strength,
                    'description': description,
                    'up_ratio': up_ratio,
                    'amount': total_amount
                })
        
        except Exception:
            continue
    
    # 按强度排序
    signals.sort(key=lambda x: x['strength'], reverse=True)
    
    # 生成建议
    recommendation = ''
    if signals:
        top_signal = signals[0]
        if top_signal['type'] == '强势启动':
            recommendation = f"关注{top_signal['sector']}板块，强度{top_signal['strength']:.1%}"
        elif top_signal['type'] == '超跌反弹':
            recommendation = f"{top_signal['sector']}板块可能反弹，谨慎参与"
        else:
            recommendation = "板块分化，关注龙头股"
    
    return {
        'signals': signals[:10],
        'recommendation': recommendation,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


@safe_call
def sector_stock_correlation(
    client: QuotationClient,
    stock_code: str,
    days: int = 20
) -> Dict[str, Any]:
    """
    个股与板块相关性分析
    
    Args:
        client: 通达信客户端
        stock_code: 股票代码
        days: 分析天数
    
    Returns:
        {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'related_sectors': [
                {
                    'name': '银行',
                    'correlation': 0.85,
                    'type': '高度相关'
                }
            ]
        }
    """
    # 获取股票所属板块
    stock_info = client.get_security_info(stock_code)
    
    if not stock_info:
        return {'error': '无法获取股票信息', 'stock_code': stock_code}
    
    # 获取所有板块
    sectors_data = client.get_block_info(BLOCK_FILE_TYPE.INDUSTRY)
    
    related_sectors = []
    
    for sector in sectors_data:
        sector_code = sector.get('code', '')
        sector_name = sector.get('name', '')
        
        try:
            stocks = client.get_block_stock_quotes(sector_code, BLOCK_FILE_TYPE.INDUSTRY)
            
            # 检查股票是否在该板块中
            is_in_sector = any(s.get('code') == stock_code for s in stocks)
            
            if is_in_sector:
                related_sectors.append({
                    'name': sector_name,
                    'code': sector_code,
                    'type': '所属板块',
                    'correlation': 1.0
                })
            else:
                # 计算相关性（简化版）
                # 实际应该用历史数据计算相关系数
                pass
        
        except Exception:
            continue
    
    return {
        'stock_code': stock_code,
        'stock_name': stock_info.get('name', ''),
        'related_sectors': related_sectors,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# 导出工具列表
__all__ = [
    'sector_overview',
    'sector_capital_flow',
    'sector_rotation_signal',
    'sector_stock_correlation'
]
