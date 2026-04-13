# opentdx — Python TDX 量化行情数据接口

项目创意来自[`pytdx`](https://github.com/rainx/pytdx)

感谢[@rainx](https://github.com/rainx)迈出的第一步

### ✨ 声明

> 本项目为个人**学习项目，并非已完成的开箱即用的产品**，仅用于学习交流
>
> 对于数据有迫切需求的朋友，通达信新推出了[官方量化平台](https://help.tdx.com.cn/quant/)，建议食用。

> 由于项目连接的是通达信客户端明文公开的服务器，是财富趋势科技公司既有的行情软件兼容行情服务器，只是简单整理便于大家学习，**严禁**用于任何**商业用途**，更**严禁滥用接口**，对此造成的任何问题本人概不负责。

又因本项目在持续推进中，接口**难免会有大幅改动，带来的不便请予宽宥**。

> ### 应biner建议，本项目精简为基础数据接口库，mcp相关将移动到 [tdx_mcp](https://github.com/LisonEvf/tdx_mcp)
> ### 又因pytdx2库名rainx已经用了，因此本库改名为opentdx，再次致敬rainx
> ### 又又，协议基本完成解析了，后期就着力于 [tdx_mcp](https://github.com/LisonEvf/tdx_mcp)了和少量组合技接口


## 主要功能

| 功能 | 说明 | 新增 |
|------|------| -|
| 股票行情 | A股、创业板、科创板、北交所 | ✅支持北交所 | 
| 扩展行情 | 期货、港股、美股、期权等 |  |
| K线数据 | 多周期（1分/5分/日线/周线等）|  ✅支持复权、即时换手率 |
| 分时图 | 实时/历史分时数据 | |
| 排行榜 | 涨跌幅、振幅、换手率等 |  |
| 板块数据 | 行业/地区/概念板块列表及成分股 | 🌟 板块K线数据 | 
| 异动监控 | 主力监控精灵数据 | |
| F10资料 | 公司基本信息、财报 | |

## 安装

```bash
pip install opentdx

```

## 指南

```bash
opentdx doc 
```

## 快速上手

```python
from datetime import date

import pandas as pd
from opentdx.tdxClient import TdxClient
from opentdx.const import MARKET, CATEGORY, EX_MARKET, PERIOD, SORT_TYPE

if __name__ == "__main__":
  with TdxClient() as client:
    # 指数信息
    print(pd.DataFrame(client.index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001')])))
    # 股票列表（带排序过滤）
    print(pd.DataFrame(client.stock_quotes_list(CATEGORY.A, sortType=SORT_TYPE.TOTAL_AMOUNT)))
    # 股票报价
    print(pd.DataFrame(client.stock_quotes(MARKET.SZ, '000001')))
    # 获取行情全景
    for name, board in client.stock_top_board().items():
        print(f"榜单：{name}")
        print(pd.DataFrame(board))
    # 获取k线
    print(pd.DataFrame(client.stock_kline(MARKET.SZ, '000001', PERIOD.DAILY)))
    # 获取指数k线
    print(pd.DataFrame(client.stock_kline(MARKET.SH, '999999', PERIOD.MINS, times=10)))
    # 获取历史分时
    print(pd.DataFrame(client.stock_tick_chart(MARKET.SZ, '000001', date(2026, 3, 16))))
    # 获取个股F10
    print(pd.DataFrame(client.stock_f10(MARKET.SZ, '000001')))
    # 历史成交
    print(pd.DataFrame(client.stock_transaction(MARKET.SZ, '000001', date(2024, 1, 15))))
    
    # 期货K线
    print(pd.DataFrame(client.goods_kline(EX_MARKET.SH_FUTURES, 'AUL8', PERIOD.DAILY)))
    # 获取扩展市场行情列表
    print(pd.DataFrame(client.goods_quotes_list(EX_MARKET.SH_FUTURES, count=5)))
    # 获取美股K线
    print(pd.DataFrame(client.goods_kline(EX_MARKET.US_STOCK, 'TSLA', PERIOD.DAILY)))
    # 美股行情
    print(pd.DataFrame(client.goods_quotes(EX_MARKET.US_STOCK, 'TSLA')))
```

### 🌟 本项目亮点

- ✅ **整体重构**：更加简洁易读
- ✅ **协议简化**：明确了一些协议的细节，更加清晰易懂
- ✅ **自动选服**：自动检查服务器连接速度，并选择最快的服务器
- ✅ **主力监控**：新增异动消息的获取
- ✅ **板块列表**：像 `通达信`一样根据板块获取股票列表，支持 `深市`、`沪市`、`创业板`、`科创板`、`北交所`
- ✅ **扩展行情**：支持 `期货`、`期权`、`债券`、`基金`、`港股`、`美股`等行情的获取
- ✅ **交互式文档**：```python doc.py```一键开启项目探索

#量化交易 #TDX接口 #Python金融

---

[![Star History Chart](https://api.star-history.com/svg?repos=LisonEvf/opentdx&type=Date)](https://star-history.com/#LisonEvf/opentdx&Date)
