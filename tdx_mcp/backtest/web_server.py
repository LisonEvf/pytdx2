# coding=utf-8
"""
Web回测界面后端API
功能：
1. 策略列表API
2. 回测执行API
3. 结果查询API
4. 文件上传API
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import json
import os
import tempfile
from datetime import datetime
import io

# 导入回测框架
from .engine import BacktestEngine
from .strategy_base import SMAStrategy, RSIStrategy, MACDStrategy
from .advanced_strategies import (
    BollingerBandsStrategy,
    KDJStrategy,
    VolumePriceStrategy,
    MultiFactorStrategy,
    TurtleStrategy
)

# 创建FastAPI应用
app = FastAPI(title="pytdx2 回测系统", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量存储回测结果
backtest_results = {}


class BacktestRequest(BaseModel):
    """回测请求模型"""
    strategy: str
    params: Dict[str, Any]
    initial_capital: float = 1000000
    commission_rate: float = 0.0003
    slippage_rate: float = 0.0001


class StrategyInfo(BaseModel):
    """策略信息模型"""
    id: str
    name: str
    category: str
    params: List[Dict[str, Any]]
    description: str


# 策略映射
STRATEGY_MAP = {
    # 基础策略
    'sma': {
        'class': SMAStrategy,
        'name': '双均线策略',
        'category': '基础策略',
        'params': [
            {'name': 'fast_window', 'type': 'int', 'default': 10, 'description': '快线周期'},
            {'name': 'slow_window', 'type': 'int', 'default': 20, 'description': '慢线周期'}
        ],
        'description': '快线上穿慢线买入，下穿卖出'
    },
    'rsi': {
        'class': RSIStrategy,
        'name': 'RSI策略',
        'category': '基础策略',
        'params': [
            {'name': 'rsi_window', 'type': 'int', 'default': 14, 'description': 'RSI周期'},
            {'name': 'oversold', 'type': 'float', 'default': 30, 'description': '超卖阈值'},
            {'name': 'overbought', 'type': 'float', 'default': 70, 'description': '超买阈值'}
        ],
        'description': 'RSI从超卖区回升买入，从超买区回落卖出'
    },
    'macd': {
        'class': MACDStrategy,
        'name': 'MACD策略',
        'category': '基础策略',
        'params': [
            {'name': 'fast', 'type': 'int', 'default': 12, 'description': '快线周期'},
            {'name': 'slow', 'type': 'int', 'default': 26, 'description': '慢线周期'},
            {'name': 'signal', 'type': 'int', 'default': 9, 'description': '信号线周期'}
        ],
        'description': 'MACD上穿信号线买入，下穿卖出'
    },
    # 高级策略
    'bollinger': {
        'class': BollingerBandsStrategy,
        'name': '布林带策略',
        'category': '高级策略',
        'params': [
            {'name': 'window', 'type': 'int', 'default': 20, 'description': '布林带周期'},
            {'name': 'std_dev', 'type': 'float', 'default': 2.0, 'description': '标准差倍数'},
            {'name': 'mode', 'type': 'str', 'default': 'breakout', 'description': '模式(breakout/reversal)'}
        ],
        'description': '突破模式：突破上轨买入；回归模式：触及下轨买入'
    },
    'kdj': {
        'class': KDJStrategy,
        'name': 'KDJ策略',
        'category': '高级策略',
        'params': [
            {'name': 'n', 'type': 'int', 'default': 9, 'description': 'KDJ周期'},
            {'name': 'oversold', 'type': 'float', 'default': 20, 'description': '超卖阈值'},
            {'name': 'overbought', 'type': 'float', 'default': 80, 'description': '超买阈值'}
        ],
        'description': 'K上穿D且在超卖区买入，K下穿D且在超买区卖出'
    },
    'turtle': {
        'class': TurtleStrategy,
        'name': '海龟策略',
        'category': '高级策略',
        'params': [
            {'name': 'entry_window', 'type': 'int', 'default': 20, 'description': '入场周期'},
            {'name': 'exit_window', 'type': 'int', 'default': 10, 'description': '出场周期'}
        ],
        'description': '突破20日高点买入，跌破10日低点卖出'
    },
    'volume_price': {
        'class': VolumePriceStrategy,
        'name': '量价策略',
        'category': '高级策略',
        'params': [
            {'name': 'volume_ma_window', 'type': 'int', 'default': 20, 'description': '成交量均线周期'},
            {'name': 'volume_increase_threshold', 'type': 'float', 'default': 2.0, 'description': '成交量放大倍数'}
        ],
        'description': '放量上涨买入，缩量下跌卖出'
    },
    'multi_factor': {
        'class': MultiFactorStrategy,
        'name': '多因子策略',
        'category': '高级策略',
        'params': [
            {'name': 'buy_threshold', 'type': 'float', 'default': 0.6, 'description': '买入阈值'},
            {'name': 'sell_threshold', 'type': 'float', 'default': -0.6, 'description': '卖出阈值'}
        ],
        'description': '综合RSI+MACD+成交量+动量因子判断'
    }
}


@app.get("/")
async def root():
    """返回HTML界面"""
    html_file = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
    if os.path.exists(html_file):
        return FileResponse(html_file)
    else:
        return {"message": "Web界面文件未找到，请访问 /docs 查看API文档"}


@app.get("/api/strategies", response_model=List[StrategyInfo])
async def get_strategies():
    """获取所有可用策略"""
    strategies = []
    for strategy_id, info in STRATEGY_MAP.items():
        strategies.append(StrategyInfo(
            id=strategy_id,
            name=info['name'],
            category=info['category'],
            params=info['params'],
            description=info['description']
        ))
    return strategies


@app.post("/api/backtest")
async def run_backtest(
    file: UploadFile = File(...),
    strategy: str = "sma",
    params: str = "{}",
    initial_capital: float = 1000000,
    commission_rate: float = 0.0003,
    slippage_rate: float = 0.0001
):
    """
    运行回测
    
    Args:
        file: CSV文件（必须包含date, open, high, low, close, volume列）
        strategy: 策略ID
        params: JSON格式的策略参数
        initial_capital: 初始资金
        commission_rate: 手续费率
        slippage_rate: 滑点率
    
    Returns:
        回测结果ID
    """
    try:
        # 解析参数
        params_dict = json.loads(params) if params else {}
        
        # 检查策略是否存在
        if strategy not in STRATEGY_MAP:
            raise HTTPException(status_code=400, detail=f"策略不存在: {strategy}")
        
        # 读取CSV文件
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # 验证数据格式
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"CSV文件缺少列: {', '.join(missing_columns)}"
            )
        
        # 创建策略实例
        strategy_info = STRATEGY_MAP[strategy]
        strategy_class = strategy_info['class']
        strategy_instance = strategy_class(params_dict)
        
        # 创建回测引擎
        engine = BacktestEngine(
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            slippage_rate=slippage_rate
        )
        
        # 运行回测
        result = engine.run_backtest(df, strategy_instance, file.filename)
        
        # 生成结果ID
        result_id = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存结果
        backtest_results[result_id] = {
            'strategy': strategy_info['name'],
            'params': params_dict,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'result_id': result_id,
            'message': '回测完成'
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="参数格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回测失败: {str(e)}")


@app.get("/api/results/{result_id}")
async def get_result(result_id: str):
    """获取回测结果"""
    if result_id not in backtest_results:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    return backtest_results[result_id]


@app.get("/api/results/{result_id}/summary")
async def get_result_summary(result_id: str):
    """获取回测结果摘要"""
    if result_id not in backtest_results:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    result = backtest_results[result_id]['result']
    
    return {
        'strategy': backtest_results[result_id]['strategy'],
        'initial_capital': result['initial_capital'],
        'final_capital': result['final_capital'],
        'total_return': result['total_return'],
        'annual_return': result['annual_return'],
        'sharpe_ratio': result['sharpe_ratio'],
        'max_drawdown': result['max_drawdown'],
        'win_rate': result['win_rate'],
        'total_trades': result['total_trades']
    }


@app.get("/api/results/{result_id}/trades")
async def get_result_trades(result_id: str):
    """获取交易记录"""
    if result_id not in backtest_results:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    return backtest_results[result_id]['result']['trades']


@app.get("/api/results/{result_id}/equity_curve")
async def get_equity_curve(result_id: str):
    """获取资金曲线"""
    if result_id not in backtest_results:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    daily_values = backtest_results[result_id]['result']['daily_values']
    
    # 转换为图表数据格式
    equity_curve = []
    for dv in daily_values:
        equity_curve.append({
            'date': str(dv['date']),
            'total_value': dv['total_value'],
            'cash': dv['cash'],
            'position_value': dv['position_value']
        })
    
    return equity_curve


@app.delete("/api/results/{result_id}")
async def delete_result(result_id: str):
    """删除回测结果"""
    if result_id not in backtest_results:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    del backtest_results[result_id]
    return {'message': '删除成功'}


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'results_count': len(backtest_results)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
