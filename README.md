# Pytdx2 - Python TDX量化数据接口

项目创意来自[`pytdx`](https://github.com/rainx/pytdx)

感谢[@rainx](https://github.com/rainx)迈出的第一步

### ✨ 声明

> 本项目为个人**学习项目，并非已完成的开箱即用的产品**，仅用于学习交流，至于ISSUE中有朋友提到的安装不便、pip安装包等问题，非常抱歉，当前阶段不予考虑。
>
> 对于数据有迫切需求的朋友，通达信新推出了[官方量化平台](https://help.tdx.com.cn/quant/)，建议食用。

> 由于项目连接的是通达信客户端明文公开的服务器，是财富趋势科技公司既有的行情软件兼容行情服务器，只是简单整理便于大家学习，**严禁**用于任何**商业用途**，更**严禁滥用接口**，对此造成的任何问题本人概不负责。



又因本项目在持续推进中，接口难免会有大幅改动，带来的不便请予宽宥。


### 🚀 1分钟快速上手

```python
# 示例代码（基于tdxClient.py）
if __name__ == "__main__":
    client = QuotationClient()
    if client.connect().login():
        log.info("获取行情列表")
        print(pd.DataFrame(client.get_security_quotes_by_category(CATEGORY.SZ)))
	      log.info("获取行情全景")
        for name, board in client.get_top_stock_board(CATEGORY.A).items():
            log.info("榜单：%s", name)
            print(pd.DataFrame(board))
        log.info("获取k线")
        print(pd.DataFrame(client.get_KLine_data(MARKET.SZ, '000001', KLINE_TYPE.DAY)))
        log.info("获取指数k线")
        print(pd.DataFrame(client.get_KLine_data(MARKET.SH, '999999', KLINE_TYPE.DAY, 0, 2000)))
```

### 🌟 本项目亮点

- ✅ **整体重构**：更加简洁易读
- ✅ **协议简化**：明确了一些协议的细节，更加清晰易懂
- ✅ **自动选服**：自动检查服务器连接速度，并选择最快的服务器
- ✅ **主力监控**：新增异动消息的获取
- ✅ **板块列表**：像 `通达信`一样根据板块获取股票列表，支持 `深市`、`沪市`、`创业板`、`科创板`、`北交所`
- ✅ **扩展行情**：支持 `期货`、`期权`、`债券`、`基金`、`港股`、`美股`等行情的获取

### 📋 TODO List

- [X] backtest模块
- [X] MCP agent模块
- [X] 基于量价交易的LargeTradeModel

#量化交易 #TDX接口 #Python金融 #行情获取 #量化策略开发

---

[![Star History Chart](https://api.star-history.com/svg?repos=LisonEvf/pytdx2&type=Date)](https://star-history.com/#LisonEvf/pytdx2&Date)
