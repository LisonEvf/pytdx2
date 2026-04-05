#!/usr/bin/env python3
# coding=utf-8
"""
启动Web回测界面
Usage: python run_web.py [--host HOST] [--port PORT]
"""
import argparse
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn


def main():
    parser = argparse.ArgumentParser(description='启动pytdx2 Web回测界面')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口 (默认: 8000)')
    parser.add_argument('--reload', action='store_true', help='开发模式（自动重载）')
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                             ║
║      ██████╗ ██╗   ██╗████████╗ █████╗                     ║
║     ██╔════╝ ██║   ██║╚══██╔══╝██╔══██╗                    ║
║     ██║  ███╗██║   ██║   ██║   ███████║                    ║
║     ██║   ██║██║   ██║   ██║   ██╔══██║                    ║
║     ╚██████╔╝╚██████╔╝   ██║   ██║  ██║                    ║
║      ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝                    ║
║                                                             ║
║            pytdx2 回测系统 v1.0.0                          ║
║                                                             ║
╚════════════════════════════════════════════════════════════╝

🚀 服务器启动中...

📍 访问地址: http://{args.host}:{args.port}
📚 API文档: http://{args.host}:{args.port}/docs

💡 使用说明:
1. 准备CSV数据文件（格式: date, open, high, low, close, volume）
2. 访问Web界面上传数据
3. 选择策略并配置参数
4. 点击"开始回测"查看结果

按 Ctrl+C 停止服务器
""")
    
    try:
        uvicorn.run(
            "tdx_mcp.backtest.web_server:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")


if __name__ == '__main__':
    main()
