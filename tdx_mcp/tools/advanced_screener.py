# coding=utf-8
"""
龙虎榜和选股工具

提供龙虎榜分析和智能选股功能
"""

from typing import Dict, List, Any
from tdx_mcp.const import MARKET, CATEGORY, SORT_TYPE
from tdx_mcp.utils.log import log
from tdx_mcp.utils.retry import safe_call, calculate_safely


def dragon_tiger_list(client, date_str: str = None) -> Dict[str, Any]:
    """
    龙虎榜数据（基于异动数据）

    Args:
        client: QuotationClient 实例
        date_str: 日期字符串（可选，默认今日）

    Returns:
        Dict: {
            "stocks": [
                {
                    "code": "000001",
                    "name": "平安银行",
                    "reason": "日涨幅偏离值达7%",
                    "buy_value": 12345678,  # 买入金额
                    "sell_value": 9876543,  # 卖出金额
                    "net_value": 2469135,  # 净买入
                    "buy_seats": [...],  # 买入席位
                    "sell_seats": [...]  # 卖出席位
                },
                ...
            ],
            "total_count": 50,
            "date": "2026-04-04"
        }
    """
    try:
        from datetime import date
        target_date = date_str or date.today().isoformat()

        # 获取异动数据（龙虎榜通常是异动股票）
        stocks_data = []
        
        # 尝试从两个市场获取异动数据
        for market in [MARKET.SH, MARKET.SZ]:
            try:
                unusual_data = client.get_unusual(market, start=0, count=100)
                if unusual_data:
                    for item in unusual_data:
                        # 筛选龙虎榜相关的异动（涨停、跌停、大幅波动等）
                        desc = item.get('desc', '')
                        if any(keyword in desc for keyword in ['涨停', '跌停', '涨幅', '跌幅', '振幅', '换手']):
                            stocks_data.append({
                                'code': item.get('code', ''),
                                'name': '',  # 需要后续补充
                                'reason': desc,
                                'time': str(item.get('time', '')),
                                'value': item.get('value', 0),
                                'market': 'SH' if market == MARKET.SH else 'SZ'
                            })
            except Exception as e:
                log.warning("获取%s异动数据失败: %s", market, e)

        # 补充股票名称
        if stocks_data:
            try:
                stock_list = client.get_stock_quotes_list(CATEGORY.A, start=0, count=500)
                for stock in stocks_data:
                    for s in stock_list:
                        if s.get('code') == stock['code']:
                            stock['name'] = s.get('name', '')
                            break
            except:
                pass

        return {
            'stocks': stocks_data[:50],  # 最多返回50条
            'total_count': len(stocks_data),
            'date': target_date,
            'note': '基于异动数据模拟，实际龙虎榜需专门数据源'
        }

    except Exception as e:
        log.error("获取龙虎榜数据失败: %s", e)
        return {
            'error': str(e),
            'stocks': [],
            'total_count': 0,
            'date': date_str or ''
        }


def stock_screener(client, 
                   market: int = 6,
                   filters: Dict[str, Any] = None,
                   sort_by: str = 'change_pct',
                   limit: int = 50,
                   **kwargs) -> Dict[str, Any]:
    """
    智能选股器

    Args:
        client: QuotationClient 实例
        market: 市场分类（0=上证A, 2=深证A, 6=A股, 8=科创板, 14=创业板）
        filters: 筛选条件（可选，支持字典形式）{
            'price_min': 5.0,  # 最低价格
            'price_max': 100.0,  # 最高价格
            'change_pct_min': -5.0,  # 最低涨幅
            'change_pct_max': 10.0,  # 最高涨幅
            'volume_min': 100000,  # 最小成交量
            'turnover_min': 1.0,  # 最小换手率（%）
            'amount_min': 10000000  # 最小成交额
        }
        sort_by: 排序字段（change_pct, volume, amount, turnover）
        limit: 返回数量
        **kwargs: 直接传递筛选条件（如price_min=5.0），用于本地调用

    Returns:
        Dict: {
            "stocks": [
                {
                    "code": "000001",
                    "name": "平安银行",
                    "price": 12.35,
                    "change_pct": 2.5,
                    "volume": 12345678,
                    "amount": 152345678,
                    "turnover": 3.5,
                    "market_cap": 2400.5
                },
                ...
            ],
            "total_count": 100,
            "filtered_count": 50
        }
    """
    try:
        # 合并filters和kwargs
        filters = filters or {}
        # 如果kwargs中有筛选条件，合并到filters中
        for key in ['price_min', 'price_max', 'change_pct_min', 'change_pct_max', 
                   'volume_min', 'turnover_min', 'amount_min']:
            if key in kwargs:
                filters[key] = kwargs[key]
        
        # 获取股票列表
        stocks = client.get_stock_quotes_list(
            CATEGORY(market),
            start=0,
            count=3000,  # 获取足够多的股票
            sortType=SORT_TYPE.CODE
        )

        if not stocks:
            return {
                'error': '无法获取股票数据',
                'stocks': [],
                'total_count': 0,
                'filtered_count': 0
            }

        # 应用筛选条件
        filtered_stocks = []
        for stock in stocks:
            # 价格筛选
            price = stock.get('close', 0)
            if price == 0:
                continue
            
            if filters.get('price_min') and price < filters['price_min']:
                continue
            if filters.get('price_max') and price > filters['price_max']:
                continue

            # 涨跌幅筛选
            pre_close = stock.get('pre_close', 0)
            if pre_close == 0:
                continue
            
            change_pct = calculate_safely(price - pre_close, pre_close, 0) * 100
            
            if filters.get('change_pct_min') and change_pct < filters['change_pct_min']:
                continue
            if filters.get('change_pct_max') and change_pct > filters['change_pct_max']:
                continue

            # 成交量筛选
            volume = stock.get('vol', 0)
            if filters.get('volume_min') and volume < filters['volume_min']:
                continue

            # 成交额筛选
            amount = stock.get('amount', 0)
            if filters.get('amount_min') and amount < filters['amount_min']:
                continue

            # 换手率筛选
            turnover_str = stock.get('turnover', '0%')
            if isinstance(turnover_str, str) and '%' in turnover_str:
                turnover = float(turnover_str.replace('%', ''))
            else:
                turnover = float(turnover_str) if turnover_str else 0
            
            if filters.get('turnover_min') and turnover < filters['turnover_min']:
                continue

            # 通过所有筛选
            filtered_stocks.append({
                'code': stock.get('code', ''),
                'name': stock.get('name', ''),
                'price': round(price, 2),
                'change_pct': round(change_pct, 2),
                'volume': volume,
                'amount': amount,
                'turnover': round(turnover, 2),
                'pre_close': round(pre_close, 2),
                'high': round(stock.get('high', 0), 2),
                'low': round(stock.get('low', 0), 2),
                'open': round(stock.get('open', 0), 2)
            })

        # 排序
        reverse = True  # 默认降序
        if sort_by == 'change_pct':
            filtered_stocks.sort(key=lambda x: x['change_pct'], reverse=reverse)
        elif sort_by == 'volume':
            filtered_stocks.sort(key=lambda x: x['volume'], reverse=reverse)
        elif sort_by == 'amount':
            filtered_stocks.sort(key=lambda x: x['amount'], reverse=reverse)
        elif sort_by == 'turnover':
            filtered_stocks.sort(key=lambda x: x['turnover'], reverse=reverse)
        elif sort_by == 'price':
            filtered_stocks.sort(key=lambda x: x['price'], reverse=reverse)

        # 限制返回数量
        result_stocks = filtered_stocks[:limit]

        return {
            'stocks': result_stocks,
            'total_count': len(stocks),
            'filtered_count': len(filtered_stocks),
            'filters': filters,
            'sort_by': sort_by
        }

    except Exception as e:
        log.error("智能选股失败: %s", e)
        return {
            'error': str(e),
            'stocks': [],
            'total_count': 0,
            'filtered_count': 0
        }


def top_gainers(client, limit: int = 20) -> Dict[str, Any]:
    """
    涨幅榜

    Args:
        client: QuotationClient 实例
        limit: 返回数量

    Returns:
        Dict: {
            "stocks": [...],
            "timestamp": "12:20:30"
        }
    """
    try:
        board_data = client.get_stock_top_board(CATEGORY.A)
        gainers = board_data.get('increase', [])[:limit]

        stocks = []
        for item in gainers:
            stocks.append({
                'code': item.get('code', ''),
                'name': item.get('name', ''),
                'price': item.get('price', 0),
                'change_pct': item.get('value', 0),
                'market': 'SH' if item.get('market') == MARKET.SH else 'SZ'
            })

        return {
            'stocks': stocks,
            'count': len(stocks),
            'timestamp': stocks[0].get('server_time', '') if stocks else ''
        }

    except Exception as e:
        log.error("获取涨幅榜失败: %s", e)
        return {
            'error': str(e),
            'stocks': [],
            'count': 0
        }


def top_losers(client, limit: int = 20) -> Dict[str, Any]:
    """
    跌幅榜

    Args:
        client: QuotationClient 实例
        limit: 返回数量

    Returns:
        Dict: {
            "stocks": [...],
            "timestamp": "12:20:30"
        }
    """
    try:
        board_data = client.get_stock_top_board(CATEGORY.A)
        losers = board_data.get('decrease', [])[:limit]

        stocks = []
        for item in losers:
            stocks.append({
                'code': item.get('code', ''),
                'name': item.get('name', ''),
                'price': item.get('price', 0),
                'change_pct': item.get('value', 0),
                'market': 'SH' if item.get('market') == MARKET.SH else 'SZ'
            })

        return {
            'stocks': stocks,
            'count': len(stocks),
            'timestamp': stocks[0].get('server_time', '') if stocks else ''
        }

    except Exception as e:
        log.error("获取跌幅榜失败: %s", e)
        return {
            'error': str(e),
            'stocks': [],
            'count': 0
        }


def high_turnover(client, limit: int = 20) -> Dict[str, Any]:
    """
    高换手率股票

    Args:
        client: QuotationClient 实例
        limit: 返回数量

    Returns:
        Dict: {
            "stocks": [...]
        }
    """
    try:
        board_data = client.get_stock_top_board(CATEGORY.A)
        turnover_list = board_data.get('turnover', [])[:limit]

        stocks = []
        for item in turnover_list:
            stocks.append({
                'code': item.get('code', ''),
                'name': item.get('name', ''),
                'price': item.get('price', 0),
                'turnover_rate': item.get('value', 0),
                'market': 'SH' if item.get('market') == MARKET.SH else 'SZ'
            })

        return {
            'stocks': stocks,
            'count': len(stocks)
        }

    except Exception as e:
        log.error("获取高换手率股票失败: %s", e)
        return {
            'error': str(e),
            'stocks': [],
            'count': 0
        }
