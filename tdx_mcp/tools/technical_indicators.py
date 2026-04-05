"""
技术指标工具集
提供布林带收窄、量价背离、形态识别等高级技术分析工具
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from ..tdxClient import QuotationClient
from ..utils.log import log
from ..utils.retry import safe_call


def bollinger_squeeze(
    client: QuotationClient,
    market: str,
    code: str,
    period: int = 20,
    std_dev: float = 2.0,
    squeeze_threshold: float = 0.15
) -> Dict[str, Any]:
    """
    布林带收窄检测（变盘预警）
    
    Args:
        client: 通达信客户端
        market: 市场代码（SH/SZ）
        code: 股票代码
        period: 布林带周期（默认20）
        std_dev: 标准差倍数（默认2.0）
        squeeze_threshold: 收窄阈值（默认0.15，即带宽小于15%视为收窄）
    
    Returns:
        {
            'code': '000001',
            'name': '平安银行',
            'squeeze': True/False,
            'bandwidth': 0.12,  # 布林带带宽
            'upper': 12.5,
            'middle': 11.8,
            'lower': 11.1,
            'current': 11.9,
            'signal': '即将突破',  # 收窄后的突破信号
            'recommendation': '关注突破方向，向上突破买入，向下突破止损'
        }
    """
    try:
        from pytdx.hq import TdxApi
        
        # 获取K线数据（至少需要period*2根K线）
        api = client.api
        if market == 'SH':
            category = 1  # 上海
        else:
            category = 0  # 深圳
        
        # 获取日K线数据
        kline_data = api.get_security_bars(9, category, code, 0, period * 2)
        
        if not kline_data or len(kline_data) < period:
            return {
                'success': False,
                'error': f'K线数据不足，至少需要{period}根K线'
            }
        
        # 提取收盘价
        closes = np.array([k['close'] for k in kline_data])
        
        # 计算布林带
        middle = np.mean(closes[-period:])  # 中轨（MA）
        std = np.std(closes[-period:])  # 标准差
        upper = middle + std_dev * std  # 上轨
        lower = middle - std_dev * std  # 下轨
        
        # 计算布林带带宽（Bandwidth）
        bandwidth = (upper - lower) / middle
        
        # 判断是否收窄
        is_squeeze = bandwidth < squeeze_threshold
        
        # 当前价格
        current_price = closes[-1]
        
        # 判断当前价格在布林带中的位置
        position = (current_price - lower) / (upper - lower)
        
        # 生成信号
        signal = ""
        recommendation = ""
        
        if is_squeeze:
            # 判断突破方向
            if position > 0.7:
                signal = "收窄+上轨附近，可能向上突破"
                recommendation = "关注向上突破，突破上轨可考虑买入"
            elif position < 0.3:
                signal = "收窄+下轨附近，可能向下突破"
                recommendation = "警惕向下突破，跌破下轨需止损"
            else:
                signal = "布林带收窄，变盘在即"
                recommendation = "关注突破方向，向上突破买入，向下突破止损"
        
        # 获取股票名称
        stock_name = code  # 默认用代码
        try:
            from pytdx.params import TDXParams
            stock_list = api.get_stock_list(category)
            for stock in stock_list:
                if stock['code'] == code:
                    stock_name = stock.get('name', code)
                    break
        except:
            pass
        
        return {
            'success': True,
            'code': code,
            'name': stock_name,
            'squeeze': is_squeeze,
            'bandwidth': round(bandwidth, 4),
            'upper': round(upper, 2),
            'middle': round(middle, 2),
            'lower': round(lower, 2),
            'current': round(current_price, 2),
            'position': round(position, 2),
            'signal': signal,
            'recommendation': recommendation
        }
        
    except Exception as e:
        log.error(f"布林带收窄检测失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def volume_price_divergence(
    client: QuotationClient,
    market: str,
    code: str,
    lookback: int = 20
) -> Dict[str, Any]:
    """
    量价背离检测（趋势反转信号）
    
    Args:
        client: 通达信客户端
        market: 市场代码（SH/SZ）
        code: 股票代码
        lookback: 回溯周期（默认20天）
    
    Returns:
        {
            'code': '000001',
            'name': '平安银行',
            'divergence_type': '顶背离',  # 顶背离/底背离/无背离
            'price_trend': '上涨',
            'volume_trend': '下降',
            'strength': 0.7,  # 背离强度（0-1）
            'signal': '价涨量缩，顶背离',
            'recommendation': '警惕回调风险，考虑减仓'
        }
    """
    try:
        from pytdx.hq import TdxApi
        
        api = client.api
        if market == 'SH':
            category = 1
        else:
            category = 0
        
        # 获取K线数据
        kline_data = api.get_security_bars(9, category, code, 0, lookback)
        
        if not kline_data or len(kline_data) < lookback:
            return {
                'success': False,
                'error': f'K线数据不足，至少需要{lookback}根K线'
            }
        
        # 提取价格和成交量
        closes = np.array([k['close'] for k in kline_data])
        volumes = np.array([k['vol'] for k in kline_data])
        
        # 计算价格趋势（最近5天 vs 前5天）
        recent_prices = closes[-5:]
        previous_prices = closes[-10:-5]
        price_change = (recent_prices.mean() - previous_prices.mean()) / previous_prices.mean()
        
        # 计算成交量趋势
        recent_volumes = volumes[-5:]
        previous_volumes = volumes[-10:-5]
        volume_change = (recent_volumes.mean() - previous_volumes.mean()) / previous_volumes.mean()
        
        # 判断趋势方向
        price_trend = "上涨" if price_change > 0.02 else "下跌" if price_change < -0.02 else "横盘"
        volume_trend = "放量" if volume_change > 0.2 else "缩量" if volume_change < -0.2 else "平稳"
        
        # 检测量价背离
        divergence_type = "无背离"
        strength = 0.0
        signal = ""
        recommendation = ""
        
        # 顶背离：价涨量缩
        if price_change > 0.02 and volume_change < -0.2:
            divergence_type = "顶背离"
            strength = min(abs(price_change) + abs(volume_change), 1.0)
            signal = "价涨量缩，顶背离，上涨动力不足"
            recommendation = "警惕回调风险，考虑减仓或止盈"
        
        # 底背离：价跌量缩
        elif price_change < -0.02 and volume_change < -0.2:
            divergence_type = "底背离"
            strength = min(abs(price_change) + abs(volume_change), 1.0)
            signal = "价跌量缩，底背离，抛压减弱"
            recommendation = "关注企稳信号，可能见底反弹"
        
        # 价涨量增（健康上涨）
        elif price_change > 0.02 and volume_change > 0.2:
            divergence_type = "无背离"
            strength = 0.3
            signal = "价涨量增，上涨健康"
            recommendation = "趋势良好，可继续持有"
        
        # 价跌量增（恐慌下跌）
        elif price_change < -0.02 and volume_change > 0.2:
            divergence_type = "无背离"
            strength = 0.5
            signal = "价跌量增，恐慌下跌"
            recommendation = "等待企稳，不宜盲目抄底"
        
        # 获取股票名称
        stock_name = code
        try:
            stock_list = api.get_stock_list(category)
            for stock in stock_list:
                if stock['code'] == code:
                    stock_name = stock.get('name', code)
                    break
        except:
            pass
        
        return {
            'success': True,
            'code': code,
            'name': stock_name,
            'divergence_type': divergence_type,
            'price_trend': price_trend,
            'volume_trend': volume_trend,
            'price_change': round(price_change, 4),
            'volume_change': round(volume_change, 4),
            'strength': round(strength, 2),
            'signal': signal,
            'recommendation': recommendation
        }
        
    except Exception as e:
        log.error(f"量价背离检测失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def pattern_recognition(
    client: QuotationClient,
    market: str,
    code: str,
    lookback: int = 60
) -> Dict[str, Any]:
    """
    K线形态识别（头肩顶/底、W底、M头等）
    
    Args:
        client: 通达信客户端
        market: 市场代码（SH/SZ）
        code: 股票代码
        lookback: 回溯周期（默认60天）
    
    Returns:
        {
            'code': '000001',
            'name': '平安银行',
            'patterns': [
                {
                    'name': 'W底',
                    'confidence': 0.8,
                    'neckline': 12.5,
                    'target': 13.5,
                    'signal': '看涨'
                }
            ],
            'recommendation': 'W底形态，突破颈线买入'
        }
    """
    try:
        from pytdx.hq import TdxApi
        
        api = client.api
        if market == 'SH':
            category = 1
        else:
            category = 0
        
        # 获取K线数据
        kline_data = api.get_security_bars(9, category, code, 0, lookback)
        
        if not kline_data or len(kline_data) < lookback:
            return {
                'success': False,
                'error': f'K线数据不足，至少需要{lookback}根K线'
            }
        
        # 提取数据
        highs = np.array([k['high'] for k in kline_data])
        lows = np.array([k['low'] for k in kline_data])
        closes = np.array([k['close'] for k in kline_data])
        
        patterns = []
        
        # 检测W底（双底）
        w_bottom = _detect_w_bottom(lows, closes)
        if w_bottom:
            patterns.append(w_bottom)
        
        # 检测M头（双顶）
        m_top = _detect_m_top(highs, closes)
        if m_top:
            patterns.append(m_top)
        
        # 检测头肩顶
        head_shoulders_top = _detect_head_shoulders_top(highs, closes)
        if head_shoulders_top:
            patterns.append(head_shoulders_top)
        
        # 检测头肩底
        head_shoulders_bottom = _detect_head_shoulders_bottom(lows, closes)
        if head_shoulders_bottom:
            patterns.append(head_shoulders_bottom)
        
        # 生成综合建议
        recommendation = ""
        if not patterns:
            recommendation = "未发现明显K线形态"
        else:
            signals = [p['signal'] for p in patterns]
            if '看涨' in signals and '看跌' not in signals:
                recommendation = f"发现{len(patterns)}个看涨形态：{', '.join([p['name'] for p in patterns])}"
            elif '看跌' in signals and '看涨' not in signals:
                recommendation = f"发现{len(patterns)}个看跌形态：{', '.join([p['name'] for p in patterns])}"
            else:
                recommendation = f"发现{len(patterns)}个形态，信号冲突，谨慎操作"
        
        # 获取股票名称
        stock_name = code
        try:
            stock_list = api.get_stock_list(category)
            for stock in stock_list:
                if stock['code'] == code:
                    stock_name = stock.get('name', code)
                    break
        except:
            pass
        
        return {
            'success': True,
            'code': code,
            'name': stock_name,
            'patterns': patterns,
            'recommendation': recommendation
        }
        
    except Exception as e:
        log.error(f"形态识别失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def _detect_w_bottom(lows: np.ndarray, closes: np.ndarray) -> Optional[Dict[str, Any]]:
    """检测W底（双底）"""
    try:
        # 找到最近30天的两个最低点
        recent_lows = lows[-30:]
        
        # 使用局部最小值检测
        from scipy.signal import argrelmin
        min_indices = argrelmin(recent_lows, order=5)[0]
        
        if len(min_indices) < 2:
            return None
        
        # 取最后两个低点
        idx1, idx2 = min_indices[-2], min_indices[-1]
        low1, low2 = recent_lows[idx1], recent_lows[idx2]
        
        # 判断是否形成W底
        # 两个低点价格接近（相差不超过3%）
        if abs(low1 - low2) / low1 > 0.03:
            return None
        
        # 两个低点之间应该有一个反弹（至少5%）
        between_high = max(recent_lows[idx1:idx2])
        if (between_high - low1) / low1 < 0.05:
            return None
        
        # 颈线 = 两个低点之间的最高点
        neckline = between_high
        
        # 目标价 = 颈线 + (颈线 - 低点)
        target = neckline + (neckline - low1)
        
        # 当前价格
        current_price = closes[-1]
        
        # 判断是否突破颈线
        breakout = current_price > neckline
        
        confidence = 0.8 if breakout else 0.6
        
        return {
            'name': 'W底',
            'confidence': confidence,
            'low1': round(low1, 2),
            'low2': round(low2, 2),
            'neckline': round(neckline, 2),
            'target': round(target, 2),
            'breakout': breakout,
            'signal': '看涨',
            'description': f'双底形态，低点{round(low1, 2)}和{round(low2, 2)}，颈线{round(neckline, 2)}'
        }
        
    except Exception:
        return None


def _detect_m_top(highs: np.ndarray, closes: np.ndarray) -> Optional[Dict[str, Any]]:
    """检测M头（双顶）"""
    try:
        recent_highs = highs[-30:]
        
        from scipy.signal import argrelmax
        max_indices = argrelmax(recent_highs, order=5)[0]
        
        if len(max_indices) < 2:
            return None
        
        idx1, idx2 = max_indices[-2], max_indices[-1]
        high1, high2 = recent_highs[idx1], recent_highs[idx2]
        
        # 两个高点价格接近
        if abs(high1 - high2) / high1 > 0.03:
            return None
        
        # 两个高点之间应该有一个回调（至少5%）
        between_low = min(recent_highs[idx1:idx2])
        if (high1 - between_low) / high1 < 0.05:
            return None
        
        # 颈线 = 两个高点之间的最低点
        neckline = between_low
        
        # 目标价 = 颈线 - (高点 - 颈线)
        target = neckline - (high1 - neckline)
        
        current_price = closes[-1]
        breakdown = current_price < neckline
        
        confidence = 0.8 if breakdown else 0.6
        
        return {
            'name': 'M头',
            'confidence': confidence,
            'high1': round(high1, 2),
            'high2': round(high2, 2),
            'neckline': round(neckline, 2),
            'target': round(target, 2),
            'breakdown': breakdown,
            'signal': '看跌',
            'description': f'双顶形态，高点{round(high1, 2)}和{round(high2, 2)}，颈线{round(neckline, 2)}'
        }
        
    except Exception:
        return None


def _detect_head_shoulders_top(highs: np.ndarray, closes: np.ndarray) -> Optional[Dict[str, Any]]:
    """检测头肩顶"""
    try:
        recent_highs = highs[-40:]
        
        from scipy.signal import argrelmax
        max_indices = argrelmax(recent_highs, order=3)[0]
        
        if len(max_indices) < 3:
            return None
        
        # 取最后3个高点
        indices = max_indices[-3:]
        h1, h2, h3 = [recent_highs[i] for i in indices]
        
        # 头肩顶特征：中间高点最高，两边高点接近
        if not (h2 > h1 and h2 > h3):
            return None
        
        if abs(h1 - h3) / h1 > 0.05:
            return None
        
        # 颈线 = 两个肩膀之间的低点
        neckline = min(recent_highs[indices[0]:indices[2]])
        
        current_price = closes[-1]
        breakdown = current_price < neckline
        
        confidence = 0.7 if breakdown else 0.5
        
        return {
            'name': '头肩顶',
            'confidence': confidence,
            'left_shoulder': round(h1, 2),
            'head': round(h2, 2),
            'right_shoulder': round(h3, 2),
            'neckline': round(neckline, 2),
            'breakdown': breakdown,
            'signal': '看跌',
            'description': f'头肩顶形态，头部{round(h2, 2)}，颈线{round(neckline, 2)}'
        }
        
    except Exception:
        return None


def _detect_head_shoulders_bottom(lows: np.ndarray, closes: np.ndarray) -> Optional[Dict[str, Any]]:
    """检测头肩底"""
    try:
        recent_lows = lows[-40:]
        
        from scipy.signal import argrelmin
        min_indices = argrelmin(recent_lows, order=3)[0]
        
        if len(min_indices) < 3:
            return None
        
        indices = min_indices[-3:]
        l1, l2, l3 = [recent_lows[i] for i in indices]
        
        # 头肩底特征：中间低点最低，两边低点接近
        if not (l2 < l1 and l2 < l3):
            return None
        
        if abs(l1 - l3) / l1 > 0.05:
            return None
        
        # 颈线 = 两个肩膀之间的高点
        neckline = max(recent_lows[indices[0]:indices[2]])
        
        current_price = closes[-1]
        breakout = current_price > neckline
        
        confidence = 0.7 if breakout else 0.5
        
        return {
            'name': '头肩底',
            'confidence': confidence,
            'left_shoulder': round(l1, 2),
            'head': round(l2, 2),
            'right_shoulder': round(l3, 2),
            'neckline': round(neckline, 2),
            'breakout': breakout,
            'signal': '看涨',
            'description': f'头肩底形态，头部{round(l2, 2)}，颈线{round(neckline, 2)}'
        }
        
    except Exception:
        return None
