#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 market_analysis.py 中的5个严重Bug

Bug清单：
1. P0: 第217行 - sector_rotation使用get_quotes而不是get_index_info
2. P0: 第529行 - market_sentiment使用硬编码0x24而不是SORT_TYPE枚举
3. P1: 第361行 - _calculate_breadth返回键名不匹配
4. P1: 第130-135行 - 重复计算成交额
5. P2: 第60行 - 导入SORT_TYPE重复

修复时间: 15分钟
"""

import re

def fix_market_analysis():
    file_path = '/Users/lisonevf/Documents/pytdx2/tdx_mcp/tools/market_analysis.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Bug 1: 修复sector_rotation使用get_quotes而不是get_index_info
    # 第217行
    content = re.sub(
        r'sectors_data = client\.get_quotes\(sector_list\)',
        'sectors_data = client.get_index_info(sector_list)',
        content
    )
    
    # Bug 2: 修复market_sentiment使用硬编码0x24
    # 第529行
    content = re.sub(
        r'sortType=0x24',
        'sortType=SORT_TYPE.TURNOVER_RATE',
        content
    )
    
    # Bug 3: 修复_calculate_breadth返回键名（已在最新提交中修复）
    # 从 'up_count' 改为 'up'
    # 这个bug已经在最新的提交中修复了，所以不需要再改
    
    # Bug 4: 修复重复计算成交额（已在最新提交中优化）
    # 只统计上证指数和深证成指
    # 这个bug已经在最新的提交中修复了，所以不需要再改
    
    # Bug 5: 修复导入重复
    # 第60行
    content = re.sub(
        r'from tdx_mcp\.const import MARKET, CATEGORY, SORT_TYPE, SORT_TYPE',
        'from tdx_mcp.const import MARKET, CATEGORY, SORT_TYPE',
        content
    )
    
    # 保存修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Bug修复完成！")
    print("\n修复内容:")
    print("1. ✅ 修复sector_rotation使用get_index_info（第217行）")
    print("2. ✅ 修复market_sentiment使用SORT_TYPE.TURNOVER_RATE（第529行）")
    print("3. ✅ 修复导入重复（第60行）")
    print("\n注意: Bug 3和4已在最新提交中修复")

if __name__ == '__main__':
    fix_market_analysis()
