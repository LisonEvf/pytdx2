# pytdx2 功能增强路线图

## Phase 1: MCP体验优化（本周，4月1-7日）

### 1.1 性能优化
- [ ] 优化采样统计算法（减少API调用次数）
- [ ] 错误处理增强（重试机制、优雅降级）
- [ ] 数据验证（异常检测、完整性校验）

### 1.2 新增工具（基于现有parser）
- [ ] **stock_detail** - 个股详情（报价+F10摘要）
  - 调用: quotes_detail + company_info
  - 返回: 价格、涨跌幅、市盈率、行业、概念
  
- [ ] **capital_flow** - 资金流向（估算版）
  - 基于大单成交估算主力资金
  - 调用: history_transaction
  - 返回: 大单净流入、中单、小单统计
  
- [ ] **dragon_tiger** - 龙虎榜数据
  - 调用: board_list (龙虎榜类型)
  - 返回: 上榜股票、买入席位、净买入金额

- [ ] **hot_concepts** - 热门概念板块
  - 基于涨幅和成交量筛选
  - 调用: 板块列表 + quotes_detail
  - 返回: 涨幅前10概念板块

### 1.3 文档完善
- [ ] 每个工具添加使用示例
- [ ] 更新README（新增工具说明）
- [ ] 创建EXAMPLES.md（MCP调用示例）

---

## Phase 2: 高级功能（下周，4月8-14日）

### 2.1 选股器
- [ ] **stock_screener** - 多条件选股
  - 支持过滤: PE、PB、市值、成交量、涨跌幅
  - 支持排序: 涨幅、换手率、量比
  - 返回: 符合条件的股票列表

### 2.2 技术指标增强
- [ ] **technical_signals** - 技术信号检测
  - MACD金叉/死叉
  - KDJ超买超卖
  - RSI强弱
  - 布林带突破
  
- [ ] **support_resistance** - 支撑压力位
  - 基于近期高低点计算
  - 返回: 关键价位列表

### 2.3 数据可视化
- [ ] **export_kline_chart** - K线图导出
  - 支持ASCII字符图
  - 可选: PNG图片（需要matplotlib）

---

## Phase 3: 智能分析（下下周，4月15-21日）

### 3.1 AI增强
- [ ] **ai_market_analysis** - AI市场分析
  - 调用LLM分析技术面+资金面
  - 生成文字分析报告

### 3.2 回测框架
- [ ] **simple_backtest** - 简单回测
  - 支持MA交叉、RSI反转策略
  - 返回: 收益率、最大回撤

---

## 技术约束

### ✅ 可以使用
- 所有parser中的接口
- 本地计算和聚合
- Python标准库

### ❌ 不使用
- 缓存层（用户要求实时数据）
- Level-2行情（数据源不可用）
- WebSocket推送（非实时推送模式）

---

## 优先级

**P0（本周必须完成）**:
1. stock_detail（个股详情）
2. capital_flow（资金流向）
3. 性能优化（采样算法）

**P1（下周）**:
1. stock_screener（选股器）
2. technical_signals（技术信号）
3. hot_concepts（热门概念）

**P2（下下周）**:
1. ai_market_analysis（AI分析）
2. simple_backtest（回测框架）

---

## 成功指标

- MCP工具数量: 从4个增加到10个
- 平均响应时间: <2秒
- 用户满意度: 主动反馈好评率>80%
