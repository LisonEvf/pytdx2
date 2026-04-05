#!/usr/bin/env python3
# coding=utf-8
"""
技术指标工具测试脚本
"""

import sys
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 直接导入pytdx2
try:
    from pytdx.hq import TdxHq_API
    from tdx_mcp.tools.technical_indicators import (
        bollinger_squeeze,
        volume_price_divergence,
        pattern_recognition
    )
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装所需依赖: pip install pytdx2 numpy scipy")
    sys.exit(1)


class SimpleClient:
    """简单的客户端封装"""
    def __init__(self):
        self.api = TdxHq_API()
        self.connected = False
    
    def connect(self):
        """连接服务器"""
        # 尝试多个服务器
        servers = [
            ('119.147.212.81', 7709),
            ('14.215.128.18', 7709),
            ('59.173.18.140', 7709),
            ('180.153.39.51', 7709)
        ]
        
        for ip, port in servers:
            try:
                if self.api.connect(ip, port):
                    self.connected = True
                    print(f"✅ 连接成功: {ip}:{port}")
                    return
            except Exception as e:
                continue
        
        raise Exception("所有服务器连接失败")
    
    def disconnect(self):
        """断开连接"""
        if self.connected:
            self.api.disconnect()
            self.connected = False


def test_bollinger_squeeze():
    """测试布林带收窄检测"""
    print("\n" + "="*50)
    print("📊 测试布林带收窄检测")
    print("="*50)
    
    client = SimpleClient()
    client.connect()
    
    try:
        # 测试平安银行
        result = bollinger_squeeze(client, 'SZ', '000001')
        
        print(f"✅ 股票: {result.get('name', result['code'])}")
        print(f"   布林带收窄: {'是' if result.get('squeeze') else '否'}")
        print(f"   带宽: {result.get('bandwidth', 0):.2%}")
        print(f"   上轨: {result.get('upper', 0):.2f}")
        print(f"   中轨: {result.get('middle', 0):.2f}")
        print(f"   下轨: {result.get('lower', 0):.2f}")
        print(f"   当前价: {result.get('current', 0):.2f}")
        print(f"   信号: {result.get('signal', '无')}")
        print(f"   建议: {result.get('recommendation', '无')}")
        
        return result.get('success', False)
    finally:
        client.disconnect()


def test_volume_price_divergence():
    """测试量价背离检测"""
    print("\n" + "="*50)
    print("📊 测试量价背离检测")
    print("="*50)
    
    client = SimpleClient()
    client.connect()
    
    try:
        # 测试平安银行
        result = volume_price_divergence(client, 'SZ', '000001')
        
        print(f"✅ 股票: {result.get('name', result['code'])}")
        print(f"   背离类型: {result.get('divergence_type', '无')}")
        print(f"   价格趋势: {result.get('price_trend', '无')}")
        print(f"   成交量趋势: {result.get('volume_trend', '无')}")
        print(f"   价格变化: {result.get('price_change', 0):.2%}")
        print(f"   成交量变化: {result.get('volume_change', 0):.2%}")
        print(f"   背离强度: {result.get('strength', 0):.2f}")
        print(f"   信号: {result.get('signal', '无')}")
        print(f"   建议: {result.get('recommendation', '无')}")
        
        return result.get('success', False)
    finally:
        client.disconnect()


def test_pattern_recognition():
    """测试形态识别"""
    print("\n" + "="*50)
    print("📊 测试K线形态识别")
    print("="*50)
    
    client = SimpleClient()
    client.connect()
    
    try:
        # 测试平安银行
        result = pattern_recognition(client, 'SZ', '000001')
        
        print(f"✅ 股票: {result.get('name', result['code'])}")
        print(f"   识别到的形态数量: {len(result.get('patterns', []))}")
        
        for pattern in result.get('patterns', []):
            print(f"\n   形态: {pattern['name']}")
            print(f"   置信度: {pattern['confidence']:.2f}")
            print(f"   信号: {pattern['signal']}")
            print(f"   描述: {pattern['description']}")
        
        print(f"\n   综合建议: {result.get('recommendation', '无')}")
        
        return result.get('success', False)
    finally:
        client.disconnect()


def main():
    """主测试函数"""
    print("\n" + "🚀 "*20)
    print("开始测试技术指标工具")
    print("🚀 "*20 + "\n")
    
    start_time = time.time()
    
    # 测试所有工具
    results = {
        '布林带收窄': test_bollinger_squeeze(),
        '量价背离': test_volume_price_divergence(),
        '形态识别': test_pattern_recognition()
    }
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 输出总结
    print("\n" + "="*50)
    print("📊 测试总结")
    print("="*50)
    
    for tool, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{tool}: {status}")
    
    print(f"\n⏱️ 总耗时: {total_time:.2f}秒")
    
    # 判断是否全部通过
    all_passed = all(results.values())
    if all_passed:
        print("\n✅ 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
