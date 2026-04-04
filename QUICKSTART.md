# 快速开始指南（5分钟上手）

## 📦 安装

### 步骤1：安装Python包

```bash
pip install tdx-mcp
```

### 步骤2：配置MCP Server（Claude Desktop）

编辑Claude Desktop配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "tdx": {
      "command": "mcp-server-tdx"
    }
  }
}
```

### 步骤3：重启Claude Desktop

配置完成后重启Claude Desktop即可使用。

---

## 🚀 第一个查询

### 在Claude中提问：

```
查看今天的市场概况
```

Claude会自动调用`market_overview`工具并返回结果。

---

## 💡 常用场景

### 场景1：每日复盘

**提问**：
```
帮我分析今天的市场情况，包括：
1. 指数涨跌
2. 成交额
3. 涨跌家数
4. 市场情绪
```

**Claude会调用**：
- `market_overview()` - 市场概况
- `market_sentiment()` - 市场情绪

---

### 场景2：个股分析

**提问**：
```
分析一下平安银行（000001）的情况
```

**Claude会调用**：
- `stock_detail(0, '000001')` - 个股详情
- `capital_flow(0, '000001')` - 资金流向

---

### 场景3：智能选股

**提问**：
```
帮我筛选一些股票：
- 价格在5-30元之间
- 今天涨幅在0-5%
- 换手率大于3%
- 按涨幅排序
```

**Claude会调用**：
```python
stock_screener(
    price_min=5.0,
    price_max=30.0,
    change_pct_min=0,
    change_pct_max=5.0,
    turnover_min=3.0,
    sort_by='change_pct',
    limit=20
)
```

---

### 场景4：龙虎榜分析

**提问**：
```
今天有哪些股票上了龙虎榜？
```

**Claude会调用**：
- `dragon_tiger()` - 龙虎榜数据

---

### 场景5：技术分析

**提问**：
```
帮我分析一下平安银行的MACD和RSI指标
```

**Claude会调用**：
1. `stock_kline(0, '000001', 4, count=100)` - 获取K线
2. `indicator_macd(kline_data)` - 计算MACD
3. `indicator_rsi(kline_data, 14)` - 计算RSI

---

## 🎯 12个MCP工具速查

### 市场分析

| 工具 | 用途 | 提问示例 |
|------|------|---------|
| market_overview | 全市场概览 | "今天市场怎么样？" |
| sector_rotation | 板块轮动 | "今天哪些板块领涨？" |
| market_breadth | 市场广度 | "今天涨跌家数如何？" |
| market_sentiment | 市场情绪 | "今天市场情绪如何？" |

### 个股分析

| 工具 | 用途 | 提问示例 |
|------|------|---------|
| stock_detail | 个股详情 | "分析一下000001" |
| capital_flow | 资金流向 | "000001今天主力资金情况" |
| hot_concepts | 热门概念 | "今天哪些概念板块最火？" |

### 智能选股

| 工具 | 用途 | 提问示例 |
|------|------|---------|
| dragon_tiger | 龙虎榜 | "今天龙虎榜有哪些股票？" |
| stock_screener | 智能选股 | "筛选价格5-20元的股票" |
| top_gainers | 涨幅榜 | "今天涨幅最大的股票" |
| top_losers | 跌幅榜 | "今天跌幅最大的股票" |
| high_turnover | 高换手 | "今天换手率最高的股票" |

---

## 📊 使用示例

### Python代码调用

如果你想在Python代码中直接使用：

```python
from tdx_mcp.client.quotationClient import QuotationClient
from tdx_mcp.tools.market_analysis import market_overview
from tdx_mcp.const import MARKET

# 连接服务器
client = QuotationClient(True, True)
client.connect().login()

# 调用工具
result = market_overview(client)
print(f"上证指数: {result['indices'][0]['price']}")
print(f"成交额: {result['amount']['total']}亿")

# 断开连接
client.disconnect()
```

---

## ⚡ 性能优化

### 常见问题

**Q: 查询速度慢怎么办？**  
A: market_overview和market_breadth需要采样统计，首次查询约5-8秒，后续会更快。

**Q: 非交易时间能查吗？**  
A: 可以查询历史数据，但实时数据会有延迟或缺失。

**Q: 如何获取更准确的数据？**  
A: 建议在交易时间（9:30-15:00）使用，数据最准确。

---

## 🐛 故障排查

### 问题1：连接失败

**症状**：`ConnectionError` 或超时

**解决方案**：
1. 检查网络连接
2. 确认通达信服务器可访问
3. 尝试切换服务器

### 问题2：数据为空

**症状**：返回`None`或空列表

**解决方案**：
1. 确认股票代码正确
2. 检查是否在交易时间
3. 查看日志错误信息

### 问题3：MCP工具未加载

**症状**：Claude提示"未找到工具"

**解决方案**：
1. 确认配置文件路径正确
2. 重启Claude Desktop
3. 检查`mcp-server-tdx`命令是否可用

---

## 📚 进阶学习

- [完整API文档](./docs/API.md)
- [回测框架教程](./tdx_mcp/backtest/README.md)
- [示例策略](./examples/)
- [常见问题FAQ](./docs/FAQ.md)

---

## 💬 社区支持

- GitHub Issues: [提交问题](https://github.com/LisonEvf/pytdx2/issues)
- Discord社区: [加入讨论](https://discord.gg/clawd)

---

**5分钟上手完成！开始你的量化之旅吧！🚀**
