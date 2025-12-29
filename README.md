# Pytdx2 - Python TDX量化数据接口

项目创意来自[`pytdx`](https://github.com/rainx/pytdx)

感谢[@rainx](https://github.com/rainx)迈出的第一步

### ✨ 声明

> 本项目为个人学习项目,仅用于学习交流，严禁用于非法用途

> 由于连接的是既有的行情软件兼容行情服务器，严禁用于任何商业用途，对此造成的任何问题本人概不负责。

### 🚀 1分钟快速上手
```python
# 示例代码（基于tdxClient.py）
if __name__ == "__main__":
    client = TdxClient()
    if client.connect().login():
        log.info("获取行情列表")
        print_df(client.call(stock.QuotesList(CATEGORY.SZ, 200)))
        log.info("获取k线")
        print_df(client.get_security_bars(MARKET.SZ, '000001', KLINE_TYPE.DAY_K, 0, 500))
        log.info("获取指数k线")
        print_df(client.get_security_bars(MARKET.SH, '999999', KLINE_TYPE.DAY_K, 0, 2000))
```

### 🌟 本项目亮点

  - ✅ **整体重构**：更加简洁易读
  - ✅ **协议简化**：明确了一些协议的细节，更加清晰易懂
  - ✅ **自动选服**：自动检查服务器连接速度，并选择最快的服务器
  - ✅ **主力监控**：新增异动消息的获取
  - ✅ **板块列表**：像`通达信`一样根据板块获取股票列表，支持`深市`、`沪市`、`创业板`、`科创板`、`北交所`

### 📋 TODO List
  - [x] 提供MCP协议的接入
  - [x] 基于量价交易的LargeTradeModel
  - [x] backtest模块


#量化交易 #TDX接口 #Python金融 #行情获取 #量化策略开发


---

[![Star History Chart](https://api.star-history.com/svg?repos=LisonEvf/pytdx2&type=Date)](https://star-history.com/#LisonEvf/pytdx2&Date)