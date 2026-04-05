# pytdx2 Web回测界面

## 🎯 功能特性

- ✅ **8种内置策略**：双均线、RSI、MACD、布林带、KDJ、海龟、量价、多因子
- ✅ **实时可视化**：资金曲线、收益曲线、回撤图表
- ✅ **详细报告**：夏普比率、最大回撤、胜率等12项绩效指标
- ✅ **交互式配置**：参数实时调整，即时生效
- ✅ **拖拽上传**：支持CSV文件拖拽上传

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/lisonevf/Documents/pytdx2
pip install fastapi uvicorn python-multipart
```

### 2. 生成示例数据

```bash
python generate_sample_data.py
# 可选参数：python generate_sample_data.py 1000 sample.csv
```

### 3. 启动服务器

```bash
python run_web.py
# 或者开发模式：
python run_web.py --reload
```

### 4. 访问界面

打开浏览器访问：http://localhost:8000

## 📊 支持的策略

### 基础策略

1. **双均线策略** (SMA)
   - 参数：快线周期、慢线周期
   - 逻辑：快线上穿慢线买入，下穿卖出

2. **RSI策略**
   - 参数：RSI周期、超卖阈值、超买阈值
   - 逻辑：RSI从超卖区回升买入

3. **MACD策略**
   - 参数：快线、慢线、信号线周期
   - 逻辑：MACD上穿信号线买入

### 高级策略

4. **布林带策略**
   - 参数：周期、标准差倍数、模式
   - 模式：breakout（突破） / reversal（回归）

5. **KDJ策略**
   - 参数：KDJ周期、超卖/超买阈值
   - 逻辑：K上穿D且在超卖区买入

6. **海龟策略**
   - 参数：入场周期、出场周期
   - 逻辑：突破20日高点买入

7. **量价策略**
   - 参数：成交量均线周期、放大倍数
   - 逻辑：放量上涨买入，缩量下跌卖出

8. **多因子策略**
   - 参数：买入/卖出阈值
   - 逻辑：综合RSI+MACD+成交量+动量判断

## 📁 数据格式

CSV文件必须包含以下列：

| 列名 | 类型 | 说明 |
|------|------|------|
| date | string | 日期（YYYY-MM-DD） |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | int | 成交量 |

### 示例数据

```csv
date,open,high,low,close,volume
2023-01-01,100.00,102.50,99.50,101.20,1000000
2023-01-02,101.20,103.00,100.80,102.50,1200000
...
```

## 🎛️ API文档

访问 http://localhost:8000/docs 查看完整API文档

### 主要端点

- `GET /api/strategies` - 获取策略列表
- `POST /api/backtest` - 运行回测
- `GET /api/results/{result_id}` - 获取完整结果
- `GET /api/results/{result_id}/summary` - 获取结果摘要
- `GET /api/results/{result_id}/equity_curve` - 获取资金曲线
- `GET /api/results/{result_id}/trades` - 获取交易记录

## 💡 使用示例

### Python调用API

```python
import requests

# 1. 获取策略列表
response = requests.get('http://localhost:8000/api/strategies')
strategies = response.json()

# 2. 运行回测
with open('sample_data.csv', 'rb') as f:
    files = {'file': f}
    data = {
        'strategy': 'sma',
        'params': '{"fast_window": 10, "slow_window": 20}',
        'initial_capital': 1000000,
        'commission_rate': 0.0003
    }
    response = requests.post('http://localhost:8000/api/backtest', files=files, data=data)
    result_id = response.json()['result_id']

# 3. 获取结果
summary = requests.get(f'http://localhost:8000/api/results/{result_id}/summary').json()
print(f"总收益率: {summary['total_return']*100:.2f}%")
print(f"夏普比率: {summary['sharpe_ratio']:.2f}")
```

## 📈 绩效指标说明

| 指标 | 说明 | 优秀标准 |
|------|------|---------|
| 总收益率 | 回测期间的总收益 | > 30% |
| 年化收益率 | 年化后的收益率 | > 15% |
| 夏普比率 | 风险调整后收益 | > 1.0 |
| 最大回撤 | 从峰值到谷底的最大跌幅 | < 20% |
| 胜率 | 盈利交易占比 | > 50% |
| 交易次数 | 总交易次数 | 根据策略 |

## 🔧 配置说明

### 回测配置

- **初始资金**：默认100万元
- **手续费率**：默认0.03%
- **滑点率**：默认0.01%

### 策略参数

每个策略都有特定参数，在界面上可以实时调整。

## 🐛 常见问题

### 1. 启动失败

确保安装了所有依赖：
```bash
pip install fastapi uvicorn python-multipart pandas numpy
```

### 2. 上传失败

检查CSV格式是否正确，必须包含所有必需列。

### 3. 回测结果异常

- 检查数据质量
- 调整策略参数
- 确认交易成本设置合理

## 📝 开发说明

### 项目结构

```
pytdx2/
├── run_web.py                 # 启动脚本
├── generate_sample_data.py    # 示例数据生成
├── tdx_mcp/backtest/
│   ├── web_server.py         # Web后端API
│   ├── web/index.html        # Web前端界面
│   ├── engine.py             # 回测引擎
│   ├── strategy_base.py      # 基础策略
│   ├── advanced_strategies.py # 高级策略
│   └── risk_manager.py       # 风险管理
└── sample_data.csv           # 示例数据
```

### 自定义策略

1. 在 `advanced_strategies.py` 中添加新策略类
2. 继承 `BaseStrategy`
3. 实现 `generate_signals()` 方法
4. 在 `web_server.py` 的 `STRATEGY_MAP` 中注册

## 📞 支持

- GitHub: https://github.com/LisonEvf/pytdx2
- 问题反馈: 提交 Issue

## 📄 License

MIT License

---

**🐦‍🔥 pytdx2 - 专业量化回测平台**
