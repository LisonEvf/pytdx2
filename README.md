# Pytdx2 - Python TDX量化数据接口

项目创意来自[`pytdx`](https://github.com/rainx/pytdx)

感谢[@rainx](https://github.com/rainx)迈出的第一步

### ✨ 声明

> 本项目为个人**学习项目，并非已完成的开箱即用的产品**，仅用于学习交流，至于ISSUE中有朋友提到的安装不便、pip安装包等问题，非常抱歉，当前阶段不予考虑。
>
> 由于项目连接的是通达信客户端明文公开的服务器，是财富趋势科技公司既有的行情软件兼容行情服务器，只是简单整理便于大家学习，**严禁**用于任何**商业用途**，更**严禁滥用接口**，对此造成的任何问题本人概不负责。

又因本项目在持续推进中，接口**难免会有大幅改动，带来的不便请予宽宥。

---

## 🚀 系统要求

- **Python**: 3.12+
- **操作系统**: macOS / Linux / Windows

---

## 📦 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 TDX 客户端（可选）

```bash
# macOS
brew install tdxclient

# Linux
sudo apt-get install tdxclient
# 或
sudo yum install tdxclient
```

---

## 🚀 快速开始

### 方式 1: HTTP Server（推荐）

```bash
cd mcp
python3 mcpServer.py
```

服务器将在 `http://0.0.0.0:8000` 启动。

### 方式 2: 直接使用 TDX 客户端

```python
from client.quotationClient import QuotationClient
from const import MARKET, PERIOD

with QuotationClient() as client:
    client.connect().login()

    # 获取指数概况
    indexes = client.get_index_info([
        (MARKET.SH, '999999'),
        (MARKET.SZ, '399001')
    ])

    # 获取K线数据
    kline = client.get_kline(MARKET.SH, '600519', PERIOD.DAY, count=30)

    # 获取股票报价
    quotes = client.get_quotes(MARKET.SH, '600519')

    # 获取排行榜
    rankings = client.get_stock_top_board(CATEGORY.A)

    client.disconnect()
```

---

## 📚 API 文档

详细 API 文档请查看：[mcp/API.md](mcp/API.md)

### 主要接口

- **指数相关**: get_Index_Overview, get_index_momentum
- **股票报价**: stock_quotes
- **K线数据**: stock_kline
- **排行榜**: stock_top_board
- **板块列表**: get_top_stock
- **公司信息**: get_company_info
- **历史分时图**: get_history_tick_chart
- **历史成交**: get_history_transaction
- **历史委托**: get_history_orders
- **实时成交**: get_transaction
- **集合竞价**: get_auction
- **异动监控**: get_unusual
- **量价分布**: get_vol_profile
- **图表采样**: get_chart_sampling
- **股票列表**: get_stock_list
- **股票数量**: get_stock_count

---

## 🎯 使用示例

### Python HTTP Server 调用

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 健康检查
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 获取指数概况
response = requests.get(f"{BASE_URL}/api/get_Index_Overview")
print(response.json())

# 获取股票报价
params = {"code_list": "SH", "code": "600519"}
response = requests.post(f"{BASE_URL}/api/stock_quotes", json=params)
print(response.json())

# 获取K线数据
params = {
    "market": "SH",
    "code": "600519",
    "period": "DAILY",
    "count": 30
}
response = requests.post(f"{BASE_URL}/api/stock_kline", json=params)
print(response.json())
```

### JavaScript 调用

```javascript
const BASE_URL = 'http://localhost:8000';

// 健康检查
fetch(`${BASE_URL}/health`)
  .then(res => res.json())
  .then(data => console.log(data));

// 获取指数概况
fetch(`${BASE_URL}/api/get_Index_Overview`)
  .then(res => res.text())
  .then(json => console.log(JSON.parse(json)));
```

---

## 🌟 项目亮点

- ✅ **整体重构**：更加简洁易读
- ✅ **协议简化**：明确了一些协议的细节，更加清晰易懂
- ✅ **自动选服**：自动检查服务器连接速度，并选择最快的服务器
- ✅ **主力监控**：新增异动消息的获取
- ✅ **板块列表**：像 `通达信`一样根据板块获取股票列表，支持 `深市`、`沪市`、`创业板`、`科创板`、`北交所`
- ✅ **扩展行情**：支持 `期货`、`期权`、`债券`、`基金`、`港股`、`美股`等行情的获取
- ✅ **Python 3.12 支持**：全面适配 Python 3.12，移除 3.9 兼容性代码

---

## 📝 注意事项

1. **Python 版本**: **必须使用 Python 3.12+**
2. **网络连接**: 需要连接到通达信行情服务器
3. **商业用途**: **严禁**用于任何商业用途
4. **数据来源**: 数据来自通达信客户端明文公开的服务器

---

## 📊 支持的市场

- **上海市场**: 上证A股、上证B股、上证指数、上证50、上证180等
- **深圳市场**: 深证A股、深证B股、深证成指、创业板、中小板等
- **北交所**: 北证A股
- **扩展市场**: 期货、期权、港股、美股等

---

## 📊 支持的K线周期

- **分钟线**: 1分钟、5分钟、15分钟、30分钟、60分钟
- **日K**: 日K线
- **周K**: 周K线
- **月K**: 月K线

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [rainx/pytdx](https://github.com/rainx/pytdx) - 项目创意来源
- [OpenClaw](https://github.com/openclaw/openclaw) - OpenClaw AI Agent 框架

---

**版本**: 0.2.0 Python 3.12  
**最后更新**: 2026-03-21
