# MCP Server 接口文档

## 📋 概述

TDX MCP Server 提供了丰富的股票数据接口，支持实时行情、历史数据、技术分析等功能。

## 🔗 健康检查

### `health_check()`
检查 MCP Server 连接状态

**返回：**
```json
{
  "healthy": true,
  "message": "TDX MCP Server is running and connected"
}
```

---

## 📊 指数相关

### `get_Index_Overview()`
获取指数概况（上证、深证、北证、创业板、科创板、沪深300）

**返回：** 指数数据 JSON

### `get_index_momentum(market, code)`
获取指数动量指标

**参数：**
- `market`: MARKET (SH/SZ/BJ)
- `code`: 指数代码

**返回：** 动量指标数据

---

## 💹 股票报价

### `stock_quotes(code_list, code)`
获取股票报价

**支持三种参数形式：**
1. `stock_quotes(market, code)`
2. `stock_quotes((market, code))`
3. `stock_quotes([(market1, code1), (market2, code2)])`

**返回：** 报价数据，包含：
- 最新价、涨跌幅、涨速
- 开盘价、最高价、最低价、昨收
- 成交量、成交额
- 内盘/外盘
- 一档盘口
- 活跃度等

---

## 📈 K线数据

### `stock_kline(market, code, period, start, count, times)`
获取K线数据

**参数：**
- `market`: MARKET (SH/SZ/BJ)
- `code`: 股票代码
- `period`: PERIOD (MIN_1/MIN_5/DAILY/WEEKLY等)
- `start`: 起始位置
- `count`: 数据数量
- `times`: 多周期倍数

**返回：** K线数据，包含：
- 日期时间、开盘价、最高价、最低价、收盘价
- 成交量、成交额
- 涨跌统计

---

## 🏆 排行榜

### `stock_top_board(category)`
获取股票排行榜

**参数：**
- `category`: CATEGORY (SH/SZ/A/BJ/CYB/KCB)

**返回：** 10个榜单：
- 涨幅榜、跌幅榜
- 振幅榜、涨速榜、跌速榜
- 量比榜、换手率榜
- 委比正序、委比倒序

---

## 📋 板块股票列表

### `get_top_stock(category, start, count)`
获取板块内股票列表

**参数：**
- `category`: 板块分类
- `start`: 起始位置
- `count`: 获取数量

**返回：** 股票列表，包含详细行情数据

---

## 🏢 公司信息

### `get_company_info(market, code)`
获取公司详细信息

**返回：** 包含：
- 股票基本信息
- 除权分红信息
- 财报信息

---

## 📉 历史分时图

### `get_history_tick_chart(market, code, date)`
获取历史分时图数据

**参数：**
- `market`: MARKET
- `code`: 股票代码
- `date`: 查询日期

**返回：** 分时图数据，包含：
- 时间、价格、成交量
- 平均价

---

## 💰 历史成交

### `get_history_transaction(market, code, date)`
获取历史成交数据

**参数：**
- `market`: MARKET
- `code`: 股票代码
- `date`: 查询日期

**返回：** 成交记录

### `get_history_transaction_with_trans(market, code, date)`
获取历史成交数据（带成交额）

**参数：**
- `market`: MARKET
- `code`: 股票代码
- `date`: 查询日期

**返回：** 成交记录（包含成交额）

---

## 📝 历史委托

### `get_history_orders(market, code, date)`
获取历史委托数据

**参数：**
- `market`: MARKET
- `code`: 股票代码
- `date`: 查询日期

**返回：** 委托记录

---

## 🔄 实时成交

### `get_transaction(market, code)`
获取实时成交数据

**参数：**
- `market`: MARKET
- `code`: 股票代码

**返回：** 实时成交记录

---

## 🎯 集合竞价

### `get_auction(market, code)`
获取集合竞价数据

**参数：**
- `market`: MARKET
- `code`: 股票代码

**返回：** 集合竞价数据

---

## ⚡ 异动监控

### `get_unusual(market, start, count)`
获取异动股票列表

**参数：**
- `market`: MARKET
- `start`: 起始位置
- `count`: 获取数量

**返回：** 异动股票列表

---

## 📊 量价分布

### `get_vol_profile(market, code)`
获取量价分布数据

**参数：**
- `market`: MARKET
- `code`: 股票代码

**返回：** 量价分布数据

---

## 📈 图表采样

### `get_chart_sampling(market, code)`
获取图表采样数据

**参数：**
- `market`: MARKET
- `code`: 股票代码

**返回：** 图表采样数据

---

## 📋 股票列表

### `get_stock_list(market, start, count)`
获取股票列表

**参数：**
- `market`: MARKET
- `start`: 起始位置
- `count`: 获取数量（0表示全部）

**返回：** 股票列表

---

## 📊 股票数量

### `get_stock_count(market)`
获取股票数量

**参数：**
- `market`: MARKET

**返回：** 股票数量

---

## 🎯 使用示例

### Python 示例

```python
# 导入接口
from mcpServer import (
    health_check,
    get_Index_Overview,
    stock_quotes,
    stock_kline,
    stock_top_board,
    get_history_tick_chart,
    get_transaction
)

# 健康检查
result = health_check()
print(result)

# 获取指数概况
result = get_Index_Overview()
print(result)

# 获取股票报价
result = stock_quotes((MARKET.SH, '600519'))
print(result)

# 获取K线数据
result = stock_kline(MARKET.SH, '600519', PERIOD.DAY, count=30)
print(result)

# 获取排行榜
result = stock_top_board(CATEGORY.SH)
print(result)

# 获取历史分时图
result = get_history_tick_chart(MARKET.SH, '600519', date(2026, 3, 21))
print(result)

# 获取实时成交
result = get_transaction(MARKET.SH, '600519')
print(result)
```

### JavaScript 示例

```javascript
// 健康检查
fetch('http://localhost:8000/health')
  .then(res => res.json())
  .then(data => console.log(data));

// 获取指数概况
fetch('http://localhost:8000/tools/get_Index_Overview')
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
3. **数据格式**: 所有接口返回 JSON 字符串格式
4. **性能优化**: 单例模式管理连接，避免重复创建

---

**版本**: 0.2.0  
**最后更新**: 2026-03-21
