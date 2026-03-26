# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Pytdx2 是一个 Python TDX（通达信）量化数据接口，提供 A股、期货、港股、美股等市场行情数据，同时实现了 MCP Server 供 AI 助手调用。

## 常用命令

```bash
# 本地安装（开发模式）
pip install -e .

# 运行 MCP Server
mcp-server-tdx
# 或
python -m tdx_mcp.mcpServer

# 测试客户端（直接运行）
python tdx_mcp/tdxClient.py
```

## 架构

```
tdx_mcp/
├── client/               # 客户端实现
│   ├── baseStockClient.py    # 基类：连接管理、心跳、重试
│   ├── quotationClient.py    # A股行情（沪深北交所）
│   └── exQuotationClient.py  # 扩展行情（期货/港股/美股/期权）
├── parser/               # 协议解析器
│   ├── baseParser.py         # 基类：序列化/反序列化
│   ├── quotation/            # A股协议解析器
│   └── ex_quotation/         # 扩展市场协议解析器
├── const.py              # 枚举常量（MARKET/CATEGORY/PERIOD等）
├── tdxClient.py          # 统一客户端封装（TdxClient）
└── mcpServer.py          # MCP Server 暴露的工具函数
```

## 核心组件

### 客户端层次
- `BaseStockClient`: 管理 socket 连接、自动选服（多线程测延迟）、心跳保活、自动重试
- `QuotationClient` / `exQuotationClient`: 继承基类，调用解析器获取数据

### 解析器模式
每个解析器继承 `BaseParser`，通过 `@register_parser(msg_id, ...)` 装饰器注册协议号。调用流程：
```python
client.call(parser)  # parser.serialize() → 发送 → parser.deserialize()
```

### MCP Server
使用 FastMCP 框架，提供两类资源：
- **Resources**: 配置信息（市场代码、分类、周期等）
- **Tools**: 数据获取函数（stock_kline, stock_quotes 等）+ 技术指标计算（indicator_ma, indicator_macd 等）

## 关键枚举（const.py）

| 枚举 | 说明 | 常用值 |
|------|------|--------|
| `MARKET` | 市场 | SZ=0, SH=1, BJ=2 |
| `CATEGORY` | 分类 | A=6, KCB=8, CYB=14, BJ=12 |
| `PERIOD` | K线周期 | MIN_1=7, MIN_5=0, DAILY=4 |
| `EX_CATEGORY` | 扩展市场 | SH_FUTURES=30, US_STOCK=74, HK_STOCK=71 |
| `SORT_TYPE` | 排序 | CHANGE_PCT=0xe, TOTAL_AMOUNT=0xa |

## 使用示例

```python
from tdx_mcp import TdxClient, MARKET, CATEGORY, PERIOD

with TdxClient() as client:
    # K线
    client.stock_kline(MARKET.SZ, '000001', PERIOD.DAILY)
    # 行情列表
    client.stock_quotes_list(CATEGORY.A, sortType=SORT_TYPE.TOTAL_AMOUNT)
    # 期货
    client.goods_kline(EX_CATEGORY.SH_FUTURES, 'AUL8', PERIOD.DAILY)
```

## 发布

包名：`tdx-mcp`，通过 GitHub Actions 自动发布到 PyPI。
