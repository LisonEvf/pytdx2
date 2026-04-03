"""复权和换手率计算模块"""
from datetime import datetime
from typing import Literal, Optional, Union
from tdx_mcp.utils.log import log


AdjustType = Literal["none", "qfq", "hfq"]  # 不复权、前复权、后复权


def calc_adjust_factor_for_qfq(xdxr_list: list[dict], target_date: datetime) -> float:
    """
    计算前复权因子
    前复权：保持当前价格不变，调整历史价格
    公式：前复权价 = (原价 - 每股分红 + 配股价×配股比例) / (1 + 送转股比例 + 配股比例)

    Args:
        xdxr_list: 除权除息数据列表
        target_date: 目标日期（K线日期）

    Returns:
        float: 累积复权因子
    """
    if not xdxr_list:
        return 1.0

    # 筛选出目标日期之后的除权事件（前复权是向后累积）
    future_xdxr = [
        x for x in xdxr_list
        if x.get('date') and isinstance(x['date'], datetime) and x['date'] > target_date
    ]

    if not future_xdxr:
        return 1.0

    # 按日期升序排序（从早到晚）
    future_xdxr.sort(key=lambda x: x['date'])

    # 累积计算复权因子
    total_factor = 1.0
    for xdxr in future_xdxr:
        # 每股分红（fenhong 是每10股派现，需要除以10）
        fenhong = xdxr.get('fenhong') or 0
        dividend = fenhong / 10.0

        # 送转股比例（songzhuangu 是每10股送转，需要除以10）
        songzhuangu = xdxr.get('songzhuangu') or 0
        bonus_ratio = songzhuangu / 10.0

        # 配股比例（peigu 是每10股配股，需要除以10）
        peigu = xdxr.get('peigu') or 0
        allot_ratio = peigu / 10.0

        # 配股价
        peigujia = xdxr.get('peigujia') or 0

        # 计算单次复权因子
        if (1 + bonus_ratio + allot_ratio) != 0:
            factor = (1 - dividend + peigujia * allot_ratio) / (1 + bonus_ratio + allot_ratio)
            total_factor *= factor

    return total_factor


def calc_adjust_factor_for_hfq(xdxr_list: list[dict], target_date: datetime) -> float:
    """
    计算后复权因子
    后复权：保持历史价格不变，调整当前价格
    公式：后复权价 = 原价 × (1 + 送转股比例 + 配股比例) - 配股价×配股比例 + 每股分红

    Args:
        xdxr_list: 除权除息数据列表
        target_date: 目标日期（K线日期）

    Returns:
        float: 累积复权因子
    """
    if not xdxr_list:
        return 1.0

    # 筛选出目标日期之前的除权事件（后复权是向前累积）
    past_xdxr = [
        x for x in xdxr_list
        if x.get('date') and isinstance(x['date'], datetime) and x['date'] <= target_date
    ]

    if not past_xdxr:
        return 1.0

    # 按日期降序排序（从晚到早）
    past_xdxr.sort(key=lambda x: x['date'], reverse=True)

    # 累积计算复权因子
    total_factor = 1.0
    for xdxr in past_xdxr:
        # 每股分红
        fenhong = xdxr.get('fenhong') or 0
        dividend = fenhong / 10.0

        # 送转股比例
        songzhuangu = xdxr.get('songzhuangu') or 0
        bonus_ratio = songzhuangu / 10.0

        # 配股比例
        peigu = xdxr.get('peigu') or 0
        allot_ratio = peigu / 10.0

        # 配股价
        peigujia = xdxr.get('peigujia') or 0

        # 计算单次复权因子（后复权是前复权的逆运算）
        if (1 - dividend + peigujia * allot_ratio) != 0:
            factor = (1 + bonus_ratio + allot_ratio) / (1 - dividend + peigujia * allot_ratio)
            total_factor *= factor

    return total_factor


def apply_adjustment(kline_data: list[dict], xdxr_list: list[dict],
                     adjust_type: AdjustType) -> list[dict]:
    """
    应用复权调整到 K 线数据

    Args:
        kline_data: K线数据列表
        xdxr_list: 除权除息数据列表
        adjust_type: 复权类型（none/qfq/hfq）

    Returns:
        list[dict]: 调整后的 K 线数据
    """
    if adjust_type == "none" or not xdxr_list:
        return kline_data

    adjusted_data = []
    for bar in kline_data:
        bar_copy = bar.copy()
        target_date = bar.get('datetime') or bar.get('date_time')

        if target_date is None:
            adjusted_data.append(bar_copy)
            continue

        # 计算复权因子
        if adjust_type == "qfq":
            factor = calc_adjust_factor_for_qfq(xdxr_list, target_date)
        else:  # hfq
            factor = calc_adjust_factor_for_hfq(xdxr_list, target_date)

        # 应用到价格字段
        for field in ['open', 'high', 'low', 'close']:
            if field in bar_copy and bar_copy[field] is not None:
                bar_copy[field] = round(bar_copy[field] * factor, 2)

        # 标记复权类型
        bar_copy['adjust_type'] = adjust_type
        bar_copy['adjust_factor'] = round(factor, 6)

        adjusted_data.append(bar_copy)

    return adjusted_data


def calc_turnover(vol: Union[int, float], float_shares: float) -> Optional[float]:
    """
    计算换手率
    换手率 = 成交量 / 流通股本 × 100

    Args:
        vol: 成交量（手）
        float_shares: 流通股本（万股）

    Returns:
        float | None: 换手率（%），如果数据无效返回 None
    """
    if vol is None or float_shares is None or float_shares <= 0:
        return None

    # vol 单位：手（1手=100股）
    # float_shares 单位：万股
    # 换手率 = (vol × 100) / (float_shares × 10000) × 100 = vol / (float_shares × 100)
    try:
        turnover = (vol * 100) / (float_shares * 10000) * 100
        return round(turnover, 2)
    except (ZeroDivisionError, TypeError):
        return None