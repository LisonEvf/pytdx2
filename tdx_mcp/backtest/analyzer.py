# coding=utf-8
"""
绩效分析

计算回测绩效指标
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np


class PerformanceAnalyzer:
    """
    绩效分析器
    
    功能：
    - 计算收益率指标
    - 计算风险指标
    - 生成回测报告
    """
    
    def __init__(self, portfolio):
        """
        初始化分析器
        
        Args:
            portfolio: Portfolio实例
        """
        self.portfolio = portfolio
        self.daily_values = portfolio.daily_values
        self.trades = portfolio.trades
    
    def analyze(self) -> Dict:
        """
        执行全面绩效分析
        
        Returns:
            Dict: {
                'returns': {
                    'total_return': float,      # 总收益率
                    'annualized_return': float, # 年化收益率
                    'daily_return_avg': float   # 日均收益率
                },
                'risk': {
                    'max_drawdown': float,      # 最大回撤
                    'volatility': float,        # 年化波动率
                    'downside_volatility': float # 下行波动率
                },
                'ratios': {
                    'sharpe_ratio': float,      # 夏普比率
                    'sortino_ratio': float,     # 索提诺比率
                    'calmar_ratio': float       # 卡玛比率
                },
                'trades': {
                    'total_trades': int,        # 总交易次数
                    'win_rate': float,          # 胜率
                    'avg_profit': float,        # 平均盈利
                    'avg_loss': float,          # 平均亏损
                    'profit_factor': float      # 盈利因子
                },
                'summary': str                 # 绩效摘要
            }
        """
        if not self.daily_values:
            return {'error': '无净值数据'}
        
        df = pd.DataFrame(self.daily_values)
        
        # 计算收益率
        returns = self._calculate_returns(df)
        
        # 计算风险指标
        risk = self._calculate_risk(df, returns)
        
        # 计算风险调整比率
        ratios = self._calculate_ratios(returns, risk)
        
        # 分析交易
        trades_stats = self._analyze_trades()
        
        # 生成摘要
        summary = self._generate_summary(returns, risk, ratios, trades_stats)
        
        return {
            'returns': returns,
            'risk': risk,
            'ratios': ratios,
            'trades': trades_stats,
            'summary': summary
        }
    
    def _calculate_returns(self, df: pd.DataFrame) -> Dict:
        """计算收益率指标"""
        total_return = (df['total_value'].iloc[-1] / df['total_value'].iloc[0] - 1) * 100
        
        # 年化收益率
        days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
        annualized_return = (pow(1 + total_return / 100, 252 / max(days, 1), 1) - 1) * 100
        
        # 日均收益率
        daily_returns = df['total_value'].pct_change().dropna()
        daily_return_avg = daily_returns.mean() * 100
        
        return {
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),
            'daily_return_avg': round(daily_return_avg, 4)
        }
    
    def _calculate_risk(self, df: pd.DataFrame, returns: Dict) -> Dict:
        """计算风险指标"""
        # 最大回撤
        cummax = df['total_value'].cummax()
        drawdown = (df['total_value'] - cummax) / cummax
        max_drawdown = abs(drawdown.min()) * 100
        
        # 年化波动率
        daily_returns = df['total_value'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100
        
        # 下行波动率（仅计算负收益）
        downside_returns = daily_returns[daily_returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252) * 100 if len(downside_returns) > 0 else 0
        
        return {
            'max_drawdown': round(max_drawdown, 2),
            'volatility': round(volatility, 2),
            'downside_volatility': round(downside_volatility, 2)
        }
    
    def _calculate_ratios(self, returns: Dict, risk: Dict) -> Dict:
        """计算风险调整比率"""
        # 夏普比率（假设无风险利率3%）
        risk_free_rate = 3.0
        excess_return = returns['annualized_return'] - risk_free_rate
        sharpe_ratio = excess_return / risk['volatility'] if risk['volatility'] > 0 else 0
        
        # 索提诺比率
        sortino_ratio = excess_return / risk['downside_volatility'] if risk['downside_volatility'] > 0 else 0
        
        # 卡玛比率
        calmar_ratio = returns['annualized_return'] / risk['max_drawdown'] if risk['max_drawdown'] > 0 else 1
        
        return {
            'sharpe_ratio': round(sharpe_ratio, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'calmar_ratio': round(calmar_ratio, 2)
        }
    
    def _analyze_trades(self) -> Dict:
        """分析交易记录"""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        
        # 统计盈利和亏损交易
        profits = [t for t in self.trades if t.get('pnl', 0) > 0]
        losses = [t for t in self.trades if t.get('pnl', 0) < 0]
        
        total_trades = len(self.trades)
        win_rate = len(profits) / total_trades * 100 if total_trades > 0 else 0
        
        avg_profit = np.mean([t['pnl'] for t in profits]) if profits else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        
        # 盈利因子
        total_profit = sum(t['pnl'] for t in profits)
        total_loss = abs(sum(t['pnl'] for t in losses))
        profit_factor = total_profit / total_loss if total_loss > 0 else 1
        
        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2)
        }
    
    def _generate_summary(self, returns: Dict, risk: Dict, ratios: Dict, trades: Dict) -> str:
        """生成绩效摘要"""
        summary_lines = []
        
        # 收益率总结
        if returns['total_return'] > 0:
            summary_lines.append(f"✅ 总收益率: {returns['total_return']}%")
        else:
            summary_lines.append(f"❌ 总收益率: {returns['total_return']}%")
        
        # 风险总结
        if risk['max_drawdown'] > 20:
            summary_lines.append(f"⚠️ 最大回撤: {risk['max_drawdown']}% (高风险)")
        else:
            summary_lines.append(f"✅ 最大回撤: {risk['max_drawdown']}%")
        
        # 夏普比率总结
        if ratios['sharpe_ratio'] > 1:
            summary_lines.append(f"✅ 夏普比率: {ratios['sharpe_ratio']} (优秀)")
        elif ratios['sharpe_ratio'] > 0.5:
            summary_lines.append(f"⚠️ 夏普比率: {ratios['sharpe_ratio']} (一般)")
        else:
            summary_lines.append(f"❌ 夏普比率: {ratios['sharpe_ratio']} (较差)")
        
        # 交易总结
        summary_lines.append(f"📊 交易次数: {trades['total_trades']}次")
        if trades['win_rate'] > 50:
            summary_lines.append(f"✅ 胜率: {trades['win_rate']}%")
        else:
            summary_lines.append(f"⚠️ 胜率: {trades['win_rate']}%")
        
        return '\n'.join(summary_lines)
    
    def generate_report(self, output_path: str = None) -> str:
        """
        生成详细回测报告
        
        Args:
            output_path: 输出文件路径（可选）
        
        Returns:
            str: 回测报告文本
        """
        analysis = self.analyze()
        
        report_lines = [
            "=" * 60,
            "回测报告".center(50),
            "=" * 60,
            "",
            "一、收益率指标",
            f"  总收益率: {analysis['returns']['total_return']}%",
            f"  年化收益率: {analysis['returns']['annualized_return']}%",
            f"  日均收益率: {analysis['returns']['daily_return_avg']}%",
            "",
            "二、风险指标",
            f"  最大回撤: {analysis['risk']['max_drawdown']}%",
            f"  年化波动率: {analysis['risk']['volatility']}%",
            f"  下行波动率: {analysis['risk']['downside_volatility']}%",
            "",
            "三、风险调整比率",
            f"  夏普比率: {analysis['ratios']['sharpe_ratio']}",
            f"  索提诺比率: {analysis['ratios']['sortino_ratio']}",
            f"  卡玛比率: {analysis['ratios']['calmar_ratio']}",
            "",
            "四、交易统计",
            f"  总交易次数: {analysis['trades']['total_trades']}",
            f"  胜率: {analysis['trades']['win_rate']}%",
            f"  平均盈利: {analysis['trades']['avg_profit']}",
            f"  平均亏损: {analysis['trades']['avg_loss']}",
            f"  盈利因子: {analysis['trades']['profit_factor']}",
            "",
            "五、绩效摘要",
            analysis['summary'],
            "",
            "=" * 60
        ]
        
        report = '\n'.join(report_lines)
        
        # 保存到文件
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report


# 数学函数
from math import pow
