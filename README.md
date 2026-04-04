# Pytdx2 - Python TDX量化数据接口

[![MCP Server](https://img.shields.io/badge/MCP-Server-blue)](https://modelcontextprotocol.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**🚀 支持MCP协议的量化数据接口 - AI助手原生集成**

项目创意来自[`pytdx`](https://github.com/rainx/pytdx)，感谢[@rainx](https://github.com/rainx)迈出的第一步

---

## ✨ 核心特性

- ✅ **MCP原生支持** - Claude、Cursor、OpenClaw等AI助手直接调用
- ✅ **12个MCP工具** - 市场分析、个股分析、智能选股全覆盖
- ✅ **开箱即用** - 10行代码接入，无需复杂配置
- ✅ **实时数据** - 连接通达信服务器，获取实时行情
- ✅ **Tick级回测** - 支持逐tick精确回测框架

---

## 📦 安装

### 方式一：MCP Server（推荐）

```bash
pip install tdx-mcp
```

在Claude Desktop配置中添加：

```json
{
  "mcpServers": {
    "tdx": {
      "command": "mcp-server-tdx"
    }
  }
}
```

### 方式二：本地开发

```bash
git clone https://github.com/LisonEvf/pytdx2.git
cd pytdx2
pip install -e .
```

---

## 🚀 快速开始（5分钟）

### 1. 市场分析

```python
# 全市场概览
from tdx_mcp.backtest import BacktestEngine

result = market_overview()
print(f"上证指数: {result['indices'][0]['price']}")
print(f"成交额: {result['amount']['total']}亿")
```

### 2. 个股分析

```python
# 查看平安银行详情
detail = stock_detail(market=0, code='000001')
print(f"名称: {detail['basic']['name']}")
print(f"市盈率: {detail['quote']['pe_ratio']}")
print(f"主力净流入: {detail['financial']['main_net_inflow']}")
```

### 3. 智能选股

```python
# 筛选条件：价格5-50元，涨幅>2%，换手率>3%
stocks = stock_screener(
    price_min=5.0,
    price_max=50.0,
    change_pct_min=2.0,
    turnover_min=3.0,
    limit=20
)

for stock in stocks['stocks']:
    print(f"{stock['code']} {stock['name']} 涨幅{stock['change_pct']}%")
```

---

## 📚 MCP工具列表（12个）

### 市场分析（4个）

| 工具 | 功能 | 示例 |
|------|------|------|
| **market_overview** | 全市场概览（指数+成交额+涨跌分布） | `market_overview()` |
| **sector_rotation** | 板块轮动（领涨/领跌股票） | `sector_rotation()` |
| **market_breadth** | 市场广度（涨跌家数+分布） | `market_breadth()` |
| **market_sentiment** | 市场情绪（热度+换手率） | `market_sentiment()` |

### 个股分析（3个）

| 工具 | 功能 | 示例 |
|------|------|------|
| **stock_detail** | 个股详情（报价+财务+估值） | `stock_detail(0, '000001')` |
| **capital_flow** | 资金流向（大单/中单/小单） | `capital_flow(0, '000001')` |
| **hot_concepts** | 热门概念（涨幅+热度评分） | `hot_concepts(top_n=10)` |

### 智能选股（5个）

| 工具 | 功能 | 示例 |
|------|------|------|
| **dragon_tiger** | 龙虎榜（异动股票） | `dragon_tiger()` |
| **stock_screener** | 智能选股器（多条件筛选） | `stock_screener(price_min=5.0)` |
| **top_gainers** | 涨幅榜 | `top_gainers(limit=20)` |
| **top_losers** | 跌幅榜 | `top_losers(limit=20)` |
| **high_turnover** | 高换手率股票 | `high_turnover(limit=20)` |

---

## 💡 使用示例

### 示例1：每日市场复盘

```python
# 1. 全市场概览
overview = market_overview()
print(f"两市成交额: {overview['amount']['total']}亿")
print(f"上涨{overview['breadth']['up']}家，下跌{overview['breadth']['down']}家")

# 2. 板块轮动
rotation = sector_rotation()
print(f"领涨股票: {rotation['top_gainers'][0]['name']}")

# 3. 市场情绪
sentiment = market_sentiment()
print(f"市场热度: {sentiment['market_heat']}, 评分: {sentiment['heat_score']}")
```

### 示例2：筛选潜力股

```python
# 筛选条件：
# - 价格5-30元
# - 涨幅0-5%（避免追高）
# - 换手率>3%（活跃）
# - 成交额>1亿（流动性好）

result = stock_screener(
    price_min=5.0,
    price_max=30.0,
    change_pct_min=0,
    change_pct_max=5.0,
    turnover_min=3.0,
    amount_min=100000000,
    sort_by='turnover',
    limit=30
)

print(f"筛选出{result['filtered_count']}只股票")
for stock in result['stocks'][:10]:
    print(f"{stock['code']} {stock['name']} 涨幅{stock['change_pct']}% 换手{stock['turnover']}%")
```

### 示例3：资金流向分析

```python
# 查看某只股票的主力资金动向
flow = capital_flow(market=0, code='000001')

if flow['main_net_inflow'] > 0:
    print(f"主力净流入{flow['main_net_inflow']/10000:.2f}万，{flow['assessment']}")
else:
    print(f"主力净流出{abs(flow['main_net_inflow'])/10000:.2f}万，{flow['assessment']}")

print(f"主力占比: {flow['main_ratio']*100:.1f}%")
```

### 示例4：Tick级回测

```python
from tdx_mcp.backtest import BacktestEngine, BaseStrategy
from datetime import date

class MyStrategy(BaseStrategy):
    def init(self, context):
        context.stock = '000001.SZ'
    
    def handle_tick(self, context, tick):
        # 监控大单买入
        if tick['volume'] > 100000:
            context.order_target_percent(context.stock, 0.8)

# 运行回测
engine = BacktestEngine(initial_capital=1000000)
result = engine.run_tick(
    start_date=date(2024, 3, 1),
    end_date=date(2024, 3, 31),
    stock_code='000001.SZ',
    strategy=MyStrategy()
)

print(result['analysis']['summary'])
```

---

## 🛠️ 高级功能

### 技术指标计算

```python
# 获取K线数据
kline = stock_kline(market=0, code='000001', period=4, count=100)

# 计算MACD
macd = indicator_macd(kline['data'])
print(f"DIF: {macd['DIF'][-1]}, DEA: {macd['DEA'][-1]}")

# 计算RSI
rsi = indicator_rsi(kline['data'], period=14)
print(f"RSI: {rsi[-1]}")

# 计算布林带
boll = indicator_boll(kline['data'])
print(f"上轨: {boll['UPPER'][-1]}, 下轨: {boll['LOWER'][-1]}")
```

### 龙虎榜分析

```python
# 查看今日异动股票
dragon = dragon_tiger()

for stock in dragon['stocks'][:10]:
    print(f"{stock['code']} {stock['name']}")
    print(f"  原因: {stock['reason']}")
    print(f"  异动值: {stock['value']}")
```

---

## 📖 API文档

### 市场分析

#### `market_overview()`
获取全市场概览数据

**返回**：
- `indices`: 主要指数行情（上证、深证、创业板等）
- `breadth`: 涨跌分布（上涨/下跌/平盘家数）
- `amount`: 成交额（上海/深圳/总额）

#### `market_breadth()`
市场广度分析

**返回**：
- `up/down/flat`: 涨跌平家数
- `limit_up/limit_down`: 涨跌停数
- `distribution`: 涨跌幅分布
- `strength`: 市场强度（0-1）

### 个股分析

#### `stock_detail(market, code)`
个股全景分析

**参数**：
- `market`: 0=深圳, 1=上海
- `code`: 股票代码（6位）

**返回**：
- `basic`: 基本信息（名称/行业/地区）
- `quote`: 行情数据（价格/涨跌/换手率）
- `financial`: 财务指标（PE/PB/ROE/市值）

#### `capital_flow(market, code)`
资金流向分析

**返回**：
- `main_net_inflow`: 主力净流入（元）
- `super_large/large/medium/small`: 分级资金流向
- `main_ratio`: 主力占比
- `assessment`: 资金评估（主力流入/流出/平衡）

### 智能选股

#### `stock_screener(...)`
多条件智能选股

**参数**：
- `market`: 市场分类（0=上证A, 2=深证A, 6=A股）
- `price_min/max`: 价格区间
- `change_pct_min/max`: 涨幅区间
- `volume_min`: 最小成交量
- `turnover_min`: 最小换手率
- `amount_min`: 最小成交额
- `sort_by`: 排序字段
- `limit`: 返回数量

**返回**：
- `stocks`: 筛选结果列表
- `filtered_count`: 符合条件的股票数
- `total_count`: 总股票数

---

## 🎯 性能指标

| 指标 | 数值 |
|------|------|
| 平均响应时间 | <2秒 |
| 工具总数 | 12个 |
| MCP兼容性 | 100% |
| 文档完整度 | 90% |

---

## ⚠️ 声明

> 本项目为个人**学习项目，并非已完成的开箱即用的产品**，仅用于学习交流
>
> 对于数据有迫切需求的朋友，通达信新推出了[官方量化平台](https://help.tdx.com.cn/quant/)，建议食用。

> 由于项目连接的是通达信客户端明文公开的服务器，是财富趋势科技公司既有的行情软件兼容行情服务器，只是简单整理便于大家学习，**严禁**用于任何**商业用途**，更**严禁滥用接口**，对此造成的任何问题本人概不负责。

又因本项目在持续推进中，接口**难免会有大幅改动，带来的不便请予宽宥**。

---

## 🌟 本项目亮点

- ✅ **整体重构**：更加简洁易读
- ✅ **协议简化**：明确了一些协议的细节，更加清晰易懂
- ✅ **自动选服**：自动检查服务器连接速度，并选择最快的服务器
- ✅ **主力监控**：新增异动消息的获取
- ✅ **板块列表**：像 `通达信`一样根据板块获取股票列表，支持 `深市`、`沪市`、`创业板`、`科创板`、`北交所`
- ✅ **扩展行情**：支持 `期货`、`期权`、`债券`、`基金`、`港股`、`美股`等行情的获取
- ✅ **AI适配**：MCP模块也算是能跑了，agent还算不上，将会持续优化的
- ✅ **Tick回测**：新增tick级回测框架，支持QMT代码兼容

---

## 📋 TODO List

- [x] backtest模块
- [x] 基于量价交易的LargeTradeModel
- [x] MCP Server支持
- [x] 12个MCP工具
- [ ] 更多技术指标
- [ ] 策略回测增强
- [ ] 可视化图表导出

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 License

MIT

---

#量化交易 #TDX接口 #Python金融 #MCP
