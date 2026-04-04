# coding=utf-8
"""
个股分析工具

提供基于parser接口的个股分析功能：
1. stock_detail() - 个股详情（报价+F10摘要）
2. capital_flow() - 资金流向估算
3. hot_concepts() - 热门概念板块

使用示例：
    from tdx_mcp.tools.stock_analysis import stock_detail, capital_flow
    from tdx_mcp.client.quotationClient import QuotationClient

    client = QuotationClient(True, True)
    client.connect().login()

    # 获取个股详情
    detail = stock_detail(client, MARKET.SZ, '000001')
    print(f"股票名称: {detail['name']}")
    print(f"市盈率: {detail['pe_ratio']}")

    # 获取资金流向
    flow = capital_flow(client, MARKET.SZ, '000001')
    print(f"主力净流入: {flow['main_net_inflow']}")
"""

from typing import Dict, List, Any
from tdx_mcp.const import MARKET, CATEGORY
from tdx_mcp.utils.log import log
from tdx_mcp.utils.retry import safe_call, calculate_safely


def stock_detail(client, market: MARKET, code: str) -> Dict[str, Any]:
    """
    个股详情（整合报价+F10数据）

    Args:
        client: QuotationClient 实例
        market: 市场类型（MARKET.SH / MARKET.SZ）
        code: 股票代码（6位字符串）

    Returns:
        Dict: {
            "basic": {
                "name": "平安银行",
                "code": "000001",
                "market": "SZ",
                "industry": "银行",
                "province": "广东"
            },
            "quote": {
                "price": 12.35,
                "change": 0.15,
                "change_pct": 1.23,
                "open": 12.20,
                "high": 12.50,
                "low": 12.10,
                "volume": 12345678,
                "amount": 152345678,
                "turnover_rate": 2.35,
                "pe_ratio": 6.5,
                "pb_ratio": 0.8,
                "market_cap": 2400.5,  # 总市值（亿）
                "circulation_cap": 2100.2  # 流通市值（亿）
            },
            "financial": {
                "eps": 1.85,  # 每股收益
                "bvps": 15.23,  # 每股净资产
                "roe": 12.5,  # 净资产收益率
                "total_shares": 194.05,  # 总股本（亿）
                "circulation_shares": 170.0  # 流通股本（亿）
            }
        }
    """
    try:
        # 1. 获取报价详情
        quotes_data = client.get_quotes(market, code)
        if not quotes_data or len(quotes_data) == 0:
            return {'error': '无法获取股票报价', 'code': code}

        quote = quotes_data[0] if isinstance(quotes_data, list) else quotes_data

        # 2. 获取F10财务数据
        finance_info = client.get_company_info(market, code)
        finance_data = finance_info[0] if finance_info and isinstance(finance_info, list) else {}

        # 3. 提取基础信息
        name = quote.get('name', '')
        price = quote.get('close', 0)
        pre_close = quote.get('pre_close', 0)
        change = price - pre_close
        change_pct = round((change / pre_close) * 100, 2) if pre_close != 0 else 0

        # 4. 计算估值指标（使用安全除法）
        eps = finance_data.get('每股收益', 0)
        bvps = finance_data.get('每股净资产', 0)
        total_shares = calculate_safely(finance_data.get('总股本', 0), 100000000, 0)  # 转换为亿
        circulation_shares = calculate_safely(finance_data.get('流通股本', 0), 100000000, 0)

        pe_ratio = round(calculate_safely(price, eps, 0), 2)
        pb_ratio = round(calculate_safely(price, bvps, 0), 2)
        market_cap = round(price * total_shares, 2) if total_shares > 0 else 0
        circulation_cap = round(price * circulation_shares, 2) if circulation_shares > 0 else 0

        # 5. 计算换手率（使用安全除法）
        volume = quote.get('vol', 0)
        turnover_rate = round(calculate_safely(volume, circulation_shares * 100000000, 0) * 100, 2)

        # 6. 组装结果
        result = {
            'basic': {
                'name': name,
                'code': code,
                'market': 'SH' if market == MARKET.SH else 'SZ',
                'industry': finance_data.get('行业', '未知'),
                'province': finance_data.get('地区', '未知')
            },
            'quote': {
                'price': round(price, 2),
                'change': round(change, 2),
                'change_pct': change_pct,
                'open': round(quote.get('open', 0), 2),
                'high': round(quote.get('high', 0), 2),
                'low': round(quote.get('low', 0), 2),
                'volume': volume,
                'amount': quote.get('amount', 0),
                'turnover_rate': turnover_rate,
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'market_cap': market_cap,
                'circulation_cap': circulation_cap
            },
            'financial': {
                'eps': round(eps, 2),
                'bvps': round(bvps, 2),
                'roe': round(finance_data.get('净资产收益率', 0), 2),
                'total_shares': round(total_shares, 2),
                'circulation_shares': round(circulation_shares, 2)
            }
        }

        return result

    except Exception as e:
        log.error("获取个股详情失败 %s.%s: %s", market, code, e)
        return {'error': str(e), 'code': code}


def capital_flow(client, market: MARKET, code: str, sample_days: int = 5) -> Dict[str, Any]:
    """
    资金流向估算（基于大单成交）

    Args:
        client: QuotationClient 实例
        market: 市场类型
        code: 股票代码
        sample_days: 采样天数（用于估算平均成交量）

    Returns:
        Dict: {
            "main_net_inflow": 12345678,  # 主力净流入（元）
            "super_large": 5678901,  # 特大单净流入
            "large": 6666777,  # 大单净流入
            "medium": -123456,  # 中单净流入
            "small": -234567,  # 小单净流入
            "main_ratio": 0.65,  # 主力占比
            "assessment": "主力流入"  # 评估结果
        }
    """
    try:
        # 1. 获取当日分笔成交数据
        from datetime import date
        today = date.today()
        transactions = client.get_transaction(market, code, today)

        if not transactions or len(transactions) == 0:
            return {'error': '无成交数据', 'code': code}

        # 2. 统计大单（简化版：按成交额分类）
        super_large_total = 0  # 特大单（>100万）
        large_total = 0  # 大单（20-100万）
        medium_total = 0  # 中单（5-20万）
        small_total = 0  # 小单（<5万）

        for trans in transactions:
            amount = trans.get('amount', 0)
            # action字段：BUY/SELL/NEUTRAL
            direction = trans.get('action', 'NEUTRAL')

            # 根据成交额分类
            if amount > 1000000:  # 特大单
                if direction == '买盘':
                    super_large_total += amount
                elif direction == '卖盘':
                    super_large_total -= amount
            elif amount > 200000:  # 大单
                if direction == '买盘':
                    large_total += amount
                elif direction == '卖盘':
                    large_total -= amount
            elif amount > 50000:  # 中单
                if direction == '买盘':
                    medium_total += amount
                elif direction == '卖盘':
                    medium_total -= amount
            else:  # 小单
                if direction == '买盘':
                    small_total += amount
                elif direction == '卖盘':
                    small_total -= amount

        # 3. 计算主力资金（特大单+大单）
        main_net_inflow = super_large_total + large_total
        total_net_inflow = super_large_total + large_total + medium_total + small_total
        main_ratio = round(main_net_inflow / abs(total_net_inflow), 2) if total_net_inflow != 0 else 0

        # 4. 评估资金动向（使用安全除法）
        main_net_inflow = super_large_total + large_total
        total_net_inflow = super_large_total + large_total + medium_total + small_total
        main_ratio = abs(calculate_safely(main_net_inflow, abs(total_net_inflow), 0))

        # 5. 资金评估（基于净流入金额）
        if main_net_inflow > 10000000:  # >1000万
            assessment = "主力大幅流入"
        elif main_net_inflow > 1000000:  # >100万
            assessment = "主力流入"
        elif main_net_inflow > -1000000:  # -100万 ~ 100万
            assessment = "资金平衡"
        elif main_net_inflow > -10000000:  # -1000万 ~ -100万
            assessment = "主力流出"
        else:  # <-1000万
            assessment = "主力大幅流出"

        return {
            'main_net_inflow': int(main_net_inflow),
            'super_large': int(super_large_total),
            'large': int(large_total),
            'medium': int(medium_total),
            'small': int(small_total),
            'main_ratio': main_ratio,
            'assessment': assessment
        }

    except Exception as e:
        log.error("计算资金流向失败 %s.%s: %s", market, code, e)
        return {'error': str(e), 'code': code}


def hot_concepts(client, top_n: int = 10) -> Dict[str, Any]:
    """
    热门概念板块（基于涨幅和活跃度）

    Args:
        client: QuotationClient 实例
        top_n: 返回前N个热门板块

    Returns:
        Dict: {
            "concepts": [
                {
                    "name": "DeepSeek概念",
                    "code": "BK0888",
                    "price": 1234.56,
                    "change_pct": 5.23,
                    "heat_score": 85  # 热度评分(0-100)
                },
                ...
            ],
            "market_heat": "活跃"  # 市场整体热度
        }
    """
    try:
        # 1. 获取概念板块列表（GN = 3）
        from tdx_mcp.const import BOARD_TYPE
        
        # 尝试获取概念板块数据
        # 注意：board_list返回的是板块+成分股配对数据，需要过滤
        board_data = []
        try:
            # 使用GN类型获取概念板块
            raw_boards = client.get_stock_top_board(3)  # 3 = 概念板块
            
            # 提取涨幅榜数据
            if isinstance(raw_boards, dict):
                increase_list = raw_boards.get('increase', [])
                for item in increase_list[:top_n]:
                    board_data.append({
                        'name': item.get('name', '未知'),
                        'code': item.get('code', ''),
                        'price': item.get('price', 0),
                        'change_pct': item.get('value', 0)  # value字段是涨跌幅
                    })
        except Exception as e:
            log.warning("获取概念板块失败，尝试备用方案: %s", e)
            
            # 备用方案：从涨幅榜中筛选概念相关的
            # 这里简化处理，直接返回空列表
            return {
                'error': '暂不支持概念板块数据',
                'concepts': [],
                'market_heat': '未知'
            }

        if not board_data:
            return {'error': '无法获取板块数据', 'concepts': [], 'market_heat': '未知'}

        # 2. 计算热度评分
        concepts = []
        for board in board_data:
            change_pct = board.get('change_pct', 0)
            
            # 热度评分算法
            heat_score = 0
            heat_score += min(abs(change_pct) * 5, 50)  # 涨幅贡献（最大50分）
            
            # 涨幅额外加分
            if change_pct > 5:
                heat_score += 30
            elif change_pct > 3:
                heat_score += 20
            elif change_pct > 1:
                heat_score += 10
            
            concepts.append({
                'name': board.get('name', ''),
                'code': board.get('code', ''),
                'price': board.get('price', 0),
                'change_pct': change_pct,
                'heat_score': min(heat_score, 100)
            })

        # 3. 按热度排序并取前N个
        concepts_sorted = sorted(concepts, key=lambda x: x['heat_score'], reverse=True)
        top_concepts = concepts_sorted[:top_n]

        # 4. 判断市场热度
        avg_heat = sum([c['heat_score'] for c in top_concepts]) / len(top_concepts) if top_concepts else 0
        if avg_heat >= 60:
            market_heat = "火热"
        elif avg_heat >= 40:
            market_heat = "活跃"
        elif avg_heat >= 20:
            market_heat = "温和"
        else:
            market_heat = "低迷"

        return {
            'concepts': top_concepts,
            'market_heat': market_heat
        }

    except Exception as e:
        log.error("获取热门概念失败: %s", e)
        return {'error': str(e), 'concepts': [], 'market_heat': '未知'}
