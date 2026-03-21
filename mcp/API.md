# MCP Server 接口文档（HTTP 版本）

## 📋 概述

TDX MCP Server 提供了丰富的股票数据接口，支持实时行情、历史数据、技术分析等功能。

**版本**: HTTP Server 1.0.0  
**Python 版本**: 3.9+  
**启动方式**: `python mcpServer.py`

---

## 🚀 快速开始

### 启动服务器

```bash
cd /Users/lisonevf/.openclaw/workspace/pytdx2/mcp
python mcpServer.py
```

服务器将在 `http://0.0.0.0:8000` 启动。

---

## 🔗 健康检查

### GET `/health`

检查 MCP Server 连接状态

**响应示例：**
```json
{
  "healthy": true,
  "message": "TDX MCP Server is running and connected"
}
```

---

## 📊 指数相关

### GET `/api/get_Index_Overview`

获取指数概况（上证、深证、北证、创业板、科创板、沪深300）

**响应：** 指数数据 JSON

### POST `/api/get_index_momentum`

获取指数动量指标

**参数：**
```json
{
  "market": "SH",
  "code": "999999"
}
```

**响应：** 动量指标数据

---

## 💹 股票报价

### POST `/api/stock_quotes`

获取股票报价

**参数：**
```json
{
  "code_list": "SH",
  "code": "600519"
}
```

或

```json
{
  "code_list": [
    ["SH", "600519"],
    ["SZ", "000001"]
  ]
}
```

**响应：** 报价数据，包含：
- 最新价、涨跌幅、涨速
- 开盘价、最高价、最低价、昨收
- 成交量、成交额
- 内盘/外盘
- 一档盘口
- 活跃度等

---

## 📈 K线数据

### POST `/api/stock_kline`

获取K线数据

**参数：**
```json
{
  "market": "SH",
  "code": "600519",
  "period": "DAILY",
  "start": 0,
  "count": 30,
  "times": 1
}
```

**参数说明：**
- `market`: MARKET (SH/SZ/BJ)
- `code`: 股票代码
- `period`: PERIOD (MIN_1/MIN_5/DAILY/WEEKLY等)
- `start`: 起始位置
- `count`: 数据数量
- `times`: 多周期倍数

**响应：** K线数据，包含：
- 日期时间、开盘价、最高价、最低价、收盘价
- 成交量、成交额
- 涨跌统计

---

## 🏆 排行榜

### POST `/api/stock_top_board`

获取股票排行榜

**参数：**
```json
{
  "category": "A"
}
```

**参数说明：**
- `category`: CATEGORY (SH/SZ/A/BJ/CYB/KCB)

**响应：** 10个榜单：
- 涨幅榜、跌幅榜
- 振幅榜、涨速榜、跌速榜
- 量比榜、换手率榜
- 委比正序、委比倒序

---

## 📋 板块股票列表

### POST `/api/get_top_stock`

获取板块内股票列表

**参数：**
```json
{
  "category": "A",
  "start": 0,
  "count": 80
}
```

**参数说明：**
- `category`: 板块分类
- `start`: 起始位置
- `count`: 获取数量

**响应：** 股票列表，包含详细行情数据

---

## 🏢 公司信息

### POST `/api/get_company_info`

获取公司详细信息

**参数：**
```json
{
  "market": "SH",
  "code": "600519"
}
```

**响应：** 包含：
- 股票基本信息
- 除权分红信息
- 财报信息

---

## 📉 历史分时图

### POST `/api/get_history_tick_chart`

获取历史分时图数据

**参数：**
```json
{
  "market": "SH",
  "code": "600519",
  "date": "2026-03-21"
}
```

**参数说明：**
- `market`: MARKET
- `code`: 股票代码
- `date`: 查询日期

**响应：** 分时图数据，包含：
- 时间、价格、成交量
- 平均价

---

## 💰 历史成交

### POST `/api/get_history_transaction`

获取历史成交数据

**参数：**
```json
{
  "market": "SH",
  "code": "600519",
  "date": "2026-03-21"
}
```

**参数说明：**
- `market`: MARKET
- `code`: 股票代码
- `date`: 查询日期

**响应：** 成交记录

### POST `/api/get_history_transaction_with_trans`

获取历史成交数据（带成交额）

**参数：** 同上

**响应：** 成交记录（包含成交额）

---

## 📝 历史委托

### POST `/api/get_history_orders`

获取历史委托数据

**参数：**
```json
{
  "market": "SH",
  "code": "600519",
  "date": "2026-03-21"
}
```

**参数说明：**
- `market`: MARKET
- `code`: 路票代码
- `date`: 查询日期

**响应：** 委托记录

---

## 🔄 实时成交

### POST `/api/get_transaction`

获取实时成交数据

**参数：**
```json
{
  "market": "SH",
  "code": "600519"
}
```

**参数说明：**
- `market`: MARKET
- `code`: 股票代码

**响应：** 实时成交记录

---

## 🎯 集合竞价

### POST `/api/get_auction`

获取集合竞价数据

**参数：**
```json
{
  "market": "SH",
  "code": "600519"
}
```

**参数说明：**
- `market`: MARKET
- `code`: 股票代码

**响应：** 集合竞价数据

---

## ⚡ 异动监控

### POST `/api/get_unusual`

获取异动股票列表

**参数：**
```json
{
  "market": "SH",
  "start": 0,
  "count": 20
}
```

**参数说明：**
- `market`: MARKET
- `start`: 起始位置
- `count`: 获取数量

**响应：** 异动股票列表

---

## 📊 量价分布

### POST `/api/get_vol_profile`

获取量价分布数据

**参数：**
```json
{
  "market": "SH",
  "code": "600519"
}
```

**参数说明：**
- `market`: MARKET
- `code`: 股票代码

**响应：** 量价分布数据

---

## 📈 图表采样

### POST `/api/get_chart_sampling`

获取图表采样数据

**参数：**
```json
{
  "market": "SH",
  "code": "600519"
}
```

**参数说明：**
- `market`: MARKET
- `code`: 股票代码

**响应：** 图表采样数据

---

## 📋 股票列表

### POST `/api/get_stock_list`

获取股票列表

**参数：**
```json
{
  "market": "SH",
  "start": 0,
  "count": 100
}
```

**参数说明：**
- `market`: MARKET
- `start`: 起始位置
- `count`: 获取数量（0表示全部）

**响应：** 股票列表

---

## 📊 股票数量

### POST `/api/get_stock_count`

获取股票数量

**参数：**
```json
{
  "market": "SH"
}
```

**参数说明：**
- `market`: MARKET

**响应：** 股票数量

---

## 🎯 使用示例

### Python 示例

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

# 获取排行榜
params = {"category": "A"}
response = requests.post(f"{BASE_URL}/api/stock_top_board", json=params)
print(response.json())

# 获取历史分时图
params = {
    "market": "SH",
    "code": "600519",
    "date": "2026-03-21"
}
response = requests.post(f"{BASE_URL}/api/get_history_tick_chart", json=params)
print(response.json())

# 获取实时成交
params = {"market": "SH", "code": "600519"}
response = requests.post(f"{BASE_URL}/api/get_transaction", json=params)
print(response.json())
```

### JavaScript 示例

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

// 获取股票报价
const params = { code_list: 'SH', code: '600519' };
fetch(`${BASE_URL}/api/stock_quotes`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(params)
})
  .then(res => res.text())
  .then(json => console.log(JSON.parse(json)));
```

---

## 📊 MARKET 枚举

- `SH` (0): 上海市场
- `SZ` (2): 深圳市场
- `BJ` (12): 北交所

---

## 📊 CATEGORY 枚举

- `SH` (0): 上证A股
- `SZ` (2): 深证A股
- `A` (6): 沪深A股
- `B` (7): 沪深B股
- `BJ` (12): 北证A股
- `CYB` (14): 创业板
- `KCB` (8): 科创板

---

## 📊 PERIOD 枚举

- `MIN_1` (7): 1分钟
- `MIN_5` (0): 5分钟
- `MIN_15` (1): 15分钟
- `MIN_30` (2): 30分钟
- `MIN_60` (3): 60分钟
- `DAILY` (4): 日K
- `WEEKLY` (5): 周K
- `MONTHLY` (6): 月K

---

## 🚀 启动 MCP Server

```bash
cd mcp
python mcpServer.py
```

---

## 📝 注意事项

1. **连接管理**: MCP Server 使用延迟初始化，避免模块导入时建立连接
2. **错误处理**: 所有接口都有完善的异常处理
3. **数据格式**: 所有接口返回 JSON 格式
4. **性能优化**: 单例模式管理连接，避免重复创建
5. **Python 版本**: 需要 Python 3.9+

---

## 📦 依赖

```txt
pandas>=2.0.0
numpy>=1.24.0
struct
six
zlib
logging
```

所有依赖都是标准库或常用的数据科学库。

---

**版本**: 1.0.0 HTTP Server  
**最后更新**: 2026-03-21
