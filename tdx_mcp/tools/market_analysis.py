# coding=utf-8
"""
全市场总结分析工具

提供4个MCP工具函数，用于全市场总结性分析：
1. market_overview() - 全市场概览
2. sector_rotation() - 板块轮动
3. market_breadth() - 市场广度
4. market_sentiment() - 市场情绪

使用示例：
    from tdx_mcp.tools import market_overview, sector_rotation, market_breadth, market_sentiment
    from tdx_mcp.client.quotationClient import QuotationClient

    client = QuotationClient(True, True)
    client.connect().login()

    # 获取市场概览
    overview = market_overview(client)
    print(f"上证指数: {overview['indices'][0]['price']}")

    # 获取板块轮动
    rotation = sector_rotation(client)
    print(f"领涨板块: {rotation['top_gainers']}")

    # 获取市场广度
    breadth = market_breadth(client)
    print(f"上涨家数: {breadth['up']}")

    # 获取市场情绪
    sentiment = market_sentiment(client)
    print(f"成交额: {sentiment['total_amount']}")
"""

from typing import Dict, List, Any
from tdx_mcp.const import MARKET, CATEGORY, SORT_TYPE
from tdx_mcp.utils.log import log


# ==================== 常量定义 ====================

# 主要指数代码
MAIN_INDICES = [
    (MARKET.SH, '999999', '上证指数'),
    (MARKET.SZ, '399001', '深证成指'),
    (MARKET.SZ, '399006', '创业板指'),
    (MARKET.SH, '000688', '科创50'),
    (MARKET.SH, '000300', '沪深300'),
    (MARKET.BJ, '899050', '北证50'),
]

# 行业板块指数代码（通达信行业指数）
SECTOR_INDICES = [
    (MARKET.SZ, '399190', '农林牧渔'),
    (MARKET.SZ, '399232', '采矿'),
    (MARKET.SZ, '399233', '制造业'),
    (MARKET.SZ, '399234', '水电煤气'),
    (MARKET.SZ, '399235', '建筑业'),
    (MARKET.SZ, '399236', '批发零售'),
    (MARKET.SZ, '399237', '运输仓储'),
    (MARKET.SZ, '399238', '住宿餐饮'),
    (MARKET.SZ, '399239', '信息技术'),
    (MARKET.SZ, '399240', '金融业'),
    (MARKET.SZ, '399241', '房地产'),
    (MARKET.SZ, '399242', '租赁商务'),
    (MARKET.SZ, '399243', '科研服务'),
    (MARKET.SZ, '399244', '公共环保'),
    (MARKET.SZ, '399245', '教育'),
    (MARKET.SZ, '399246', '卫生 social work'),
    (MARKET.SZ, '399247', '文体娱乐'),
    (MARKET.SZ, '399248', '综合'),
]


# ==================== 工具函数实现 ====================

def market_overview(client) -> Dict[str, Any]:
    """
    全市场概览

    返回：
    - 主要指数行情（上证、深证、创业板、科创50、沪深300、北证50）
    - 涨跌分布（上涨/下跌家数、涨停/跌停数）
    - 两市成交额

    Args:
        client: QuotationClient 实例

    Returns:
        Dict: {
            "indices": [
                {
                    "name": "上证指数",
                    "code": "999999",
                    "market": "SH",
                    "price": 3878.96,
                    "change": -1.07,
                    "change_pct": -0.03,
                    "volume": 340000000,  # 成交量
                    "amount": 49152000000  # 成交额
                },
                ...
            ],
            "breadth": {
                "up": 21,         # 上涨家数
                "down": 301,      # 下跌家数
                "flat": 1,        # 平盘家数
                "limit_up": 0,    # 涨停数
                "limit_down": 0   # 跌停数
            },
            "amount": {
                "sh": 4915.2,     # 上海成交额（亿）
                "sz": 6568.8,     # 深圳成交额（亿）
                "total": 11484    # 两市总成交额（亿）
            }
        }
    """
    try:
            # 1. 获取主要指数行情
        index_list = [(m, c) for m, c, _ in MAIN_INDICES]
        indices_data = client.get_index_info(index_list)

        indices = []
        sh_amount = 0
        sz_amount = 0

        for idx_data, (_, code, name) in zip(indices_data, MAIN_INDICES):
            market = 'SH' if idx_data['market'] == MARKET.SH else ('SZ' if idx_data['market'] == MARKET.SZ else 'BJ')

            index_info = {
                'name': name,
                'code': code,
                'market': market,
                'price': idx_data.get('close', 0),
                'change': idx_data.get('diff', 0),
                'change_pct': round((idx_data.get('diff', 0) / idx_data.get('pre_close', 1)) * 100, 2) if idx_data.get('pre_close', 0) != 0 else 0,
                'volume': idx_data.get('vol', 0),
                'amount': idx_data.get('amount', 0)
            }
            indices.append(index_info)

            # 统计成交额（只统计上证指数和深证成指，避免重复）
            if code == '999999':  # 上证指数
                sh_amount = idx_data.get('amount', 0)
            elif code == '399001':  # 深证成指
                sz_amount = idx_data.get('amount', 0)

        # 2. 获取涨跌分布（采样统计）
        breadth = _calculate_breadth(client, sample_size=300)

        # 3. 计算成交额（转换为亿）
        amount_info = {
            'sh': round(sh_amount / 100000000, 2),
            'sz': round(sz_amount / 100000000, 2),
            'total': round((sh_amount + sz_amount) / 100000000, 2)
        }

        return {
            'indices': indices,
            'breadth': breadth,
            'amount': amount_info
        }

    except Exception as e:
        log.error("获取市场概览失败: %s", e)
        return {
            'error': str(e),
            'indices': [],
            'breadth': {},
            'amount': {}
        }


def sector_rotation(client) -> Dict[str, Any]:
    """
    板块轮动分析

    返回：
    - 领涨板块前5名（行业指数）
    - 领跌板块前5名
    - 每个板块的涨跌幅

    Args:
        client: QuotationClient 实例

    Returns:
        Dict: {
            "top_gainers": [
                {
                    "name": "信息技术",
                    "code": "399239",
                    "change_pct": 2.35
                },
                ...
            ],
            "top_losers": [
                {
                    "name": "房地产",
                    "code": "399241",
                    "change_pct": -1.82
                },
                ...
            ],
            "all_sectors": [
                {
                    "name": "农林牧渔",
                    "code": "399190",
                    "price": 1234.56,
                    "change_pct": 0.45
                },
                ...
            ]
        }
    """
    try:
        # 获取板块指数行情
        sector_list = [(m, c) for m, c, _ in SECTOR_INDICES]
        sectors_data = client.get_index_info(sector_list)

        sectors = []
        for sector_data, (_, code, name) in zip(sectors_data, SECTOR_INDICES):
            price = sector_data.get('close', 0)
            pre_close = sector_data.get('pre_close', 0)
            change_pct = round(((price - pre_close) / pre_close) * 100, 2) if pre_close != 0 else 0

            sectors.append({
                'name': name,
                'code': code,
                'price': price,
                'change_pct': change_pct
            })

        # 按涨跌幅排序
        sectors_sorted = sorted(sectors, key=lambda x: x['change_pct'], reverse=True)

        # 获取领涨和领跌板块
        top_gainers = sectors_sorted[:5]
        top_losers = sectors_sorted[-5:][::-1]  # 取最后5个并反转

        return {
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'all_sectors': sectors_sorted
        }

    except Exception as e:
        log.error("获取板块轮动失败: %s", e)
        return {
            'error': str(e),
            'top_gainers': [],
            'top_losers': [],
            'all_sectors': []
        }


def market_breadth(client) -> Dict[str, Any]:
    """
    市场广度分析

    返回：
    - 涨跌家数比例
    - 涨停/跌停数
    - 涨跌幅分布（>5%, 3-5%, 0-3%, -3-0, <-5%）
    - 市场强度指标（上涨家数/总家数）

    Args:
        client: QuotationClient 实例

    Returns:
        Dict: {
            "up_count": 21,           # 上涨家数
            "down_count": 301,        # 下跌家数
            "flat_count": 1,          # 平盘家数
            "limit_up": 0,            # 涨停数
            "limit_down": 0,          # 跌停数
            "distribution": {
                "above_5": 2,         # 涨幅>5%
                "between_3_5": 5,     # 涨幅3-5%
                "between_0_3": 14,    # 涨幅0-3%
                "between_neg3_0": 180, # 跌幅0-3%
                "between_neg5_neg3": 90, # 跌幅3-5%
                "below_neg5": 31      # 跌幅<-5%
            },
            "strength": 0.065,        # 市场强度 = 上涨家数/总家数
            "breadth_ratio": 0.065    # 涨跌比 = 上涨/(上涨+下跌)
        }
    """
    try:
        # 采样统计（深市+沪市各400只）
        breadth = _calculate_breadth(client, sample_size=400, detailed=True)
        return breadth

    except Exception as e:
        log.error("获取市场广度失败: %s", e)
        return {
            'error': str(e),
            'up': 0,
            'down': 0,
            'flat': 0,
            'limit_up': 0,
            'limit_down': 0,
            'distribution': {},
            'strength': 0,
            'breadth_ratio': 0
        }


def market_sentiment(client) -> Dict[str, Any]:
    """
    市场情绪分析

    返回：
    - 两市总成交额
    - 换手率中位数（估算）
    - 量比统计（需要计算）
    - 市场热度（根据涨跌分布判断）

    Args:
        client: QuotationClient 实例

    Returns:
        Dict: {
            "total_amount": 11484,    # 两市总成交额（亿）
            "turnover_median": 2.35,  # 换手率中位数(%)
            "vol_ratio_avg": 1.05,    # 量比平均值
            "market_heat": "偏冷",    # 市场热度
            "heat_score": 25,         # 热度评分(0-100)
            "sentiment_indicators": {
                "up_ratio": 0.065,    # 上涨比例
                "limit_up_ratio": 0,  # 涨停比例
                "turnover_level": "低", # 换手率水平
                "amount_level": "缩量"  # 成交额水平
            }
        }
    """
    try:
        # 1. 获取成交额
        overview = market_overview(client)
        total_amount = overview.get('amount', {}).get('total', 0)

        # 2. 采样统计换手率和量比
        sample_data = _sample_stock_stats(client, sample_size=200)

        turnover_list = sample_data.get('turnover_list', [])
        vol_ratio_list = sample_data.get('vol_ratio_list', [])

        # 计算中位数
        turnover_median = _calculate_median(turnover_list) if turnover_list else 0
        vol_ratio_avg = round(sum(vol_ratio_list) / len(vol_ratio_list), 2) if vol_ratio_list else 0

        # 3. 计算市场热度
        breadth = overview.get('breadth', {})
        up_ratio = breadth.get('up', 0) / max(breadth.get('up', 0) + breadth.get('down', 0), 1)
        limit_up_ratio = breadth.get('limit_up', 0) / max(breadth.get('up', 0) + breadth.get('down', 0) + breadth.get('flat', 0), 1)

        # 热度评分算法（0-100）
        heat_score = 0
        heat_score += up_ratio * 40  # 上涨占比 40分
        heat_score += min(limit_up_ratio * 100, 20)  # 涨停占比 20分
        heat_score += min(turnover_median / 5 * 20, 20)  # 换手率 20分
        heat_score += min(vol_ratio_avg / 2 * 20, 20)  # 量比 20分

        # 判断市场热度
        if heat_score >= 70:
            market_heat = "火热"
        elif heat_score >= 50:
            market_heat = "活跃"
        elif heat_score >= 30:
            market_heat = "温和"
        else:
            market_heat = "偏冷"

        # 判断换手率和成交额水平
        turnover_level = "高" if turnover_median > 5 else ("中" if turnover_median > 2 else "低")
        amount_level = "放量" if total_amount > 12000 else ("正常" if total_amount > 8000 else "缩量")

        return {
            'total_amount': total_amount,
            'turnover_median': round(turnover_median, 2),
            'vol_ratio_avg': vol_ratio_avg,
            'market_heat': market_heat,
            'heat_score': round(heat_score, 1),
            'sentiment_indicators': {
                'up_ratio': round(up_ratio, 4),
                'limit_up_ratio': round(limit_up_ratio, 4),
                'turnover_level': turnover_level,
                'amount_level': amount_level
            }
        }

    except Exception as e:
        log.error("获取市场情绪失败: %s", e)
        return {
            'error': str(e),
            'total_amount': 0,
            'turnover_median': 0,
            'vol_ratio_avg': 0,
            'market_heat': '未知',
            'heat_score': 0,
            'sentiment_indicators': {}
        }


# ==================== 辅助函数 ====================

def _calculate_breadth(client, sample_size: int = 300, detailed: bool = False) -> Dict[str, Any]:
    """
    计算市场广度数据

    Args:
        client: QuotationClient 实例
        sample_size: 每个市场采样数量
        detailed: 是否返回详细分布

    Returns:
        Dict: 市场广度统计
    """
    up_count = 0
    down_count = 0
    flat_count = 0
    limit_up = 0
    limit_down = 0

    distribution = {
        'above_5': 0,        # >5%
        'between_3_5': 0,    # 3-5%
        'between_0_3': 0,    # 0-3%
        'between_neg3_0': 0, # -3-0%
        'between_neg5_neg3': 0, # -5--3%
        'below_neg5': 0      # <-5%
    }

    try:
        # 获取深市样本
        sz_quotes = client.get_stock_quotes_list(CATEGORY.SZ, start=0, count=sample_size)
        # 获取沪市样本
        sh_quotes = client.get_stock_quotes_list(CATEGORY.SH, start=0, count=sample_size)

        all_quotes = sz_quotes + sh_quotes

        for quote in all_quotes:
            price = quote.get('close', 0)
            pre_close = quote.get('pre_close', 0)

            if pre_close == 0:
                continue

            change_pct = ((price - pre_close) / pre_close) * 100

            # 涨跌统计
            if change_pct > 0.1:
                up_count += 1
            elif change_pct < -0.1:
                down_count += 1
            else:
                flat_count += 1

            # 涨跌停统计（约9.9%视为涨停/跌停）
            if change_pct >= 9.9:
                limit_up += 1
            elif change_pct <= -9.9:
                limit_down += 1

            # 分布统计
            if detailed:
                if change_pct > 5:
                    distribution['above_5'] += 1
                elif change_pct > 3:
                    distribution['between_3_5'] += 1
                elif change_pct > 0:
                    distribution['between_0_3'] += 1
                elif change_pct > -3:
                    distribution['between_neg3_0'] += 1
                elif change_pct > -5:
                    distribution['between_neg5_neg3'] += 1
                else:
                    distribution['below_neg5'] += 1

        total = up_count + down_count + flat_count
        strength = up_count / total if total > 0 else 0
        breadth_ratio = up_count / (up_count + down_count) if (up_count + down_count) > 0 else 0

        result = {
            'up': up_count,
            'down': down_count,
            'flat': flat_count,
            'limit_up': limit_up,
            'limit_down': limit_down,
            'strength': round(strength, 4),
            'breadth_ratio': round(breadth_ratio, 4)
        }

        if detailed:
            result['distribution'] = distribution

        return result

    except Exception as e:
        log.error("计算市场广度失败: %s", e)
        return {
            'up': 0,
            'down': 0,
            'flat': 0,
            'limit_up': 0,
            'limit_down': 0,
            'distribution': distribution,
            'strength': 0,
            'breadth_ratio': 0
        }


def _sample_stock_stats(client, sample_size: int = 200) -> Dict[str, List[float]]:
    """
    采样统计股票换手率和量比

    Args:
        client: QuotationClient 实例
        sample_size: 采样数量

    Returns:
        Dict: {
            'turnover_list': [2.35, 1.56, ...],
            'vol_ratio_list': [1.05, 0.98, ...]
        }
    """
    turnover_list = []
    vol_ratio_list = []

    try:
        # 获取样本（按换手率排序获取前sample_size只）
        quotes = client.get_stock_quotes_list(
            CATEGORY.A,
            start=0,
            count=sample_size,
            sortType=SORT_TYPE.TURNOVER_RATE,  # 按换手率排序
            reverse=True
        )

        for quote in quotes:
            # 换手率
            turnover_str = quote.get('turnover', '0%')
            if isinstance(turnover_str, str) and '%' in turnover_str:
                turnover = float(turnover_str.replace('%', ''))
            else:
                turnover = float(turnover_str) if turnover_str else 0
            turnover_list.append(turnover)

            # 量比（需要从其他字段估算）
            # 这里简化处理，实际量比需要历史成交量数据
            vol = quote.get('vol', 0)
            if vol > 0:
                vol_ratio_list.append(1.0)  # 默认值

        return {
            'turnover_list': turnover_list,
            'vol_ratio_list': vol_ratio_list
        }

    except Exception as e:
        log.error("采样统计失败: %s", e)
        return {
            'turnover_list': [],
            'vol_ratio_list': []
        }


def _calculate_median(data_list: List[float]) -> float:
    """
    计算中位数

    Args:
        data_list: 数据列表

    Returns:
        float: 中位数
    """
    if not data_list:
        return 0

    sorted_data = sorted(data_list)
    n = len(sorted_data)

    if n % 2 == 1:
        return sorted_data[n // 2]
    else:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
