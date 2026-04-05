#!/usr/bin/env python3
# coding=utf-8
"""
生成示例数据用于Web回测测试
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(days=500, output_file='sample_data.csv'):
    """
    生成示例股票数据
    
    Args:
        days: 天数
        output_file: 输出文件名
    """
    print(f"📊 生成 {days} 天的示例数据...")
    
    # 生成日期
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=days, freq='D')
    
    # 模拟价格数据（带趋势的随机游走）
    np.random.seed(42)
    
    close = 100  # 初始价格
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
    for i in range(days):
        # 添加趋势和周期
        trend = 0.0005 * np.sin(i / 30)  # 长期趋势
        cycle = 0.001 * np.cos(i / 10)   # 中期周期
        noise = np.random.randn() * 0.02  # 随机波动
        
        # 计算收益率
        change = trend + cycle + noise
        
        # 生成OHLC
        close = close * (1 + change)
        open_price = close * (1 + np.random.randn() * 0.005)
        high = max(open_price, close) * (1 + abs(np.random.randn() * 0.01))
        low = min(open_price, close) * (1 - abs(np.random.randn() * 0.01))
        volume = 1000000 * (1 + np.random.randn() * 0.3)
        
        opens.append(open_price)
        highs.append(high)
        lows.append(low)
        closes.append(close)
        volumes.append(int(volume))
    
    # 创建DataFrame
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'open': np.round(opens, 2),
        'high': np.round(highs, 2),
        'low': np.round(lows, 2),
        'close': np.round(closes, 2),
        'volume': volumes
    })
    
    # 保存CSV
    df.to_csv(output_file, index=False)
    
    print(f"✅ 示例数据已生成: {output_file}")
    print(f"   数据行数: {len(df)}")
    print(f"   日期范围: {df['date'].iloc[0]} ~ {df['date'].iloc[-1]}")
    print(f"   价格范围: {df['close'].min():.2f} ~ {df['close'].max():.2f}")
    print(f"\n💡 使用方法:")
    print(f"   1. 访问 http://localhost:8000")
    print(f"   2. 上传 {output_file}")
    print(f"   3. 选择策略并运行回测")
    
    return df


if __name__ == '__main__':
    import sys
    
    # 解析参数
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'sample_data.csv'
    
    generate_sample_data(days, output_file)
