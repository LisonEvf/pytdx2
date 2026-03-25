# TDX MCP Server 配置指南

## 安装

```bash
# 进入项目目录
cd pytdx2

# 安装依赖
pip install -r requirements.txt
```

## Claude Desktop 配置

在 Claude Desktop 配置文件中添加以下内容：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tdx": {
      "command": "python",
      "args": ["-m", "tdx_mcp.mcpServer"],
      "cwd": "C:/Users/Lison/Desktop/EvfWorkSpace/STOCK/TDX/pytdx2"
    }
  }
}
```

或者使用 uvx（推荐）：

```json
{
  "mcpServers": {
    "tdx": {
      "command": "uvx",
      "args": ["--directory", "C:/Users/Lison/Desktop/EvfWorkSpace/STOCK/TDX/pytdx2", "mcp-server-tdx"]
  }
}
```

## 可用工具

| 工具名 | 描述 |
|--------|------|
| `get_index_overview` | 获取指数概况（上证、深证、北证、创业、科创、沪深） |
| `stock_kline` | 获取股票K线数据 |
| `stock_tick_chart` | 获取股票分时图 |
| `stock_top_board` | 获取股票排行榜（涨幅、跌幅、振幅等） |
| `stock_quotes_list` | 获取股票行情列表 |
| `stock_quotes` | 获取股票实时报价 |
| `stock_unusual` | 获取异动数据 |
| `stock_auction` | 获取竞价数据 |
| `stock_transaction` | 获取历史成交数据 |
| `stock_f10` | 获取F10公司信息 |
| `goods_quotes_list` | 获取期货商品行情列表 |
| `goods_quotes` | 获取期货商品报价 |
| `goods_kline` | 获取期货商品K线 |
| `goods_history_transaction` | 获取期货历史成交 |
| `goods_tick_chart` | 获取期货分时图 |

## 枚举类型说明

### MARKET（市场类型）
- `SH` - 上海
- `SZ` - 深圳
- `BJ` - 北交所

### CATEGORY（市场分类）
- `A` - A股
- `B` - B股
- `SH` - 上证A
- `SZ` - 深证A
- `KCB` - 科创板
- `BJ` - 北证A
- `CYB` - 创业板

### PERIOD（K线周期）
- `MIN1` - 1分钟
- `MIN5` - 5分钟
- `MIN15` - 15分钟
- `MIN30` - 30分钟
- `MIN60` - 60分钟
- `DAY` - 日线
- `WEEK` - 周线
- `MONTH` - 月线

### EX_CATEGORY（扩展市场类别）
期货市场分类，如 `QH`（期货）、`WH`（外汇）等

## 测试运行

```bash
cd pytdx2
python -m tdx_mcp.mcpServer
```
