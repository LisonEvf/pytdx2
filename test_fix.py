#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试Bug修复效果"""

from tdx_mcp.client.quotationClient import QuotationClient
from tdx_mcp.tools.market_analysis import market_overview, sector_rotation, market_breadth, market_sentiment

def test_all():
    print("🔌 连接服务器...")
    client = QuotationClient(True, True)
    client.connect().login()
    
    print("\n📊 测试 market_overview...")
    try:
        overview = market_overview(client)
        if 'error' in overview:
            print(f"❌ 错误: {overview['error']}")
        else:
            print(f"✅ 指数数量: {len(overview.get('indices', []))}")
            print(f"✅ 涨跌分布: up={overview.get('breadth', {}).get('up', 0)}, down={overview.get('breadth', {}).get('down', 0)}")
            print(f"✅ 成交额: {overview.get('amount', {}).get('total', 0)}亿")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    print("\n📈 测试 sector_rotation...")
    try:
        rotation = sector_rotation(client)
        if 'error' in rotation:
            print(f"❌ 错误: {rotation['error']}")
        else:
            print(f"✅ 领涨板块: {len(rotation.get('top_gainers', []))}个")
            print(f"✅ 领跌板块: {len(rotation.get('top_losers', []))}个")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    print("\n📉 测试 market_breadth...")
    try:
        breadth = market_breadth(client)
        if 'error' in breadth:
            print(f"❌ 错误: {breadth['error']}")
        else:
            print(f"✅ 上涨: {breadth.get('up', 0)}, 下跌: {breadth.get('down', 0)}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    print("\n🌡️ 测试 market_sentiment...")
    try:
        sentiment = market_sentiment(client)
        if 'error' in sentiment:
            print(f"❌ 错误: {sentiment['error']}")
        else:
            print(f"✅ 成交额: {sentiment.get('total_amount', 0)}亿")
            print(f"✅ 市场热度: {sentiment.get('market_heat', '未知')}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    client.disconnect()
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_all()
