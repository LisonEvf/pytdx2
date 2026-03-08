#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 MCP Server"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp'))

from mcpServer import (
    get_Index_Overview,
    get_security_quotes,
    get_KLine_data,
    get_top_board,
    get_top_stock,
    get_company_info
)
from const import MARKET, PERIOD, CATEGORY

print('Testing MCP Server tools...')
print('=' * 60)

print('\n1. get_Index_Overview:')
try:
    result = get_Index_Overview()
    if result:
        print(f'   Success! Got {len(result)} index items')
        print(f'   Sample: {result[0]}')
    else:
        print(f'   Failed: Got empty result')
except Exception as e:
    print(f'   Failed: {e}')

print('\n2. get_security_quotes (SH 600000):')
try:
    result = get_security_quotes(MARKET.SH, '600000')
    if result:
        print(f'   Success! Got {len(result)} quote items')
        print(f'   Sample: {result[0]}')
    else:
        print(f'   Failed: Got None result')
except Exception as e:
    print(f'   Failed: {e}')

print('\n3. get_KLine_data (SZ 000001, 5min):')
try:
    result = get_KLine_data(MARKET.SZ, '000001', PERIOD.MIN_5, 0, 10)
    if result:
        print(f'   Success! Got {len(result)} kline items')
        print(f'   Sample: {result[0]}')
    else:
        print(f'   Failed: Got None result')
except Exception as e:
    print(f'   Failed: {e}')

print('\n4. get_top_board (A股):')
try:
    result = get_top_board(CATEGORY.A)
    if result:
        print(f'   Success! Got {len(result)} board categories')
        for name in list(result.keys())[:3]:
            print(f'     - {name}: {len(result[name])} items')
    else:
        print(f'   Failed: Got None result')
except Exception as e:
    print(f'   Failed: {e}')

print('\n5. get_top_stock (深证A股):')
try:
    result = get_top_stock(CATEGORY.SZ)
    if result:
        print(f'   Success! Got {len(result)} stock items')
        print(f'   Sample: {result[0]}')
    else:
        print(f'   Failed: Got None result')
except Exception as e:
    print(f'   Failed: {e}')

print('\n6. get_company_info (SH 600000):')
try:
    result = get_company_info(MARKET.SH, '600000')
    if result:
        print(f'   Success! Got company info')
        print(f'   Sample keys: {list(result.keys())[:5] if isinstance(result, dict) else result[:2]}')
    else:
        print(f'   Failed: Got None result')
except Exception as e:
    print(f'   Failed: {e}')

print('\n' + '=' * 60)
print('MCP Server testing completed!')
