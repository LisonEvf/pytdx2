# coding=utf-8
"""
可视化模块
功能：
1. K线图绘制
2. 技术指标叠加
3. 回测结果可视化
4. 报告生成
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ChartGenerator:
    """
    图表生成器
    
    功能：
    1. K线图
    2. 分时图
    3. 技术指标叠加
    4. 回测结果可视化
    """
    
    def __init__(self, style: str = 'ggplot'):
        """
        初始化图表生成器
        
        Args:
            style: matplotlib样式
        """
        self.style = style
        try:
            plt.style.use(style)
        except OSError:
            # 如果样式不可用，使用默认样式
            pass
    
    def plot_candlestick(
        self,
        data: pd.DataFrame,
        title: str = 'K线图',
        ma_periods: List[int] = None,
        volume: bool = True,
        save_path: str = None,
        figsize: Tuple[int, int] = (14, 8)
    ) -> None:
        """
        绘制K线图
        
        Args:
            data: 股票数据（必须包含date, open, high, low, close, volume）
            title: 图表标题
            ma_periods: 均线周期列表，如[5, 10, 20]
            volume: 是否显示成交量
            save_path: 保存路径
            figsize: 图表大小
        """
        df = data.copy()
        
        # 转换日期
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # 创建子图
        if volume:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, 
                                           gridspec_kw={'height_ratios': [3, 1]},
                                           sharex=True)
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=figsize)
        
        # 绘制K线
        self._draw_candlesticks(ax1, df)
        
        # 绘制均线
        if ma_periods:
            colors = ['red', 'green', 'blue', 'purple', 'orange']
            for i, period in enumerate(ma_periods):
                ma = df['close'].rolling(window=period).mean()
                color = colors[i % len(colors)]
                ax1.plot(df.index, ma, label=f'MA{period}', 
                        color=color, linewidth=1.5, alpha=0.8)
        
        # 设置标题和标签
        ax1.set_title(title, fontsize=16, fontweight='bold')
        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 绘制成交量
        if volume:
            self._draw_volume(ax2, df)
            ax2.set_ylabel('成交量', fontsize=12)
            ax2.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 图表已保存: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def _draw_candlesticks(self, ax, df: pd.DataFrame) -> None:
        """绘制K线"""
        width = 0.6
        width2 = 0.1
        
        # 定义上涨和下跌的颜色
        up_color = '#ff4136'  # 红色
        down_color = '#2ecc40'  # 绿色
        
        for i in range(len(df)):
            # 判断涨跌
            if df['close'].iloc[i] >= df['open'].iloc[i]:
                color = up_color
            else:
                color = down_color
            
            # 绘制实体
            open_price = df['open'].iloc[i]
            close_price = df['close'].iloc[i]
            high_price = df['high'].iloc[i]
            low_price = df['low'].iloc[i]
            
            # 实体
            rect = Rectangle((i - width/2, min(open_price, close_price)), 
                            width, abs(close_price - open_price),
                            facecolor=color, edgecolor=color, alpha=0.8)
            ax.add_patch(rect)
            
            # 影线
            ax.plot([i, i], [low_price, min(open_price, close_price)], 
                   color=color, linewidth=1)
            ax.plot([i, i], [max(open_price, close_price), high_price], 
                   color=color, linewidth=1)
        
        # 设置x轴
        ax.set_xlim(-1, len(df))
        
        # 设置x轴标签（日期）
        if len(df) > 20:
            step = len(df) // 10
            ax.set_xticks(range(0, len(df), step))
            ax.set_xticklabels([df.index[i].strftime('%m-%d') for i in range(0, len(df), step)], 
                              rotation=45)
        else:
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels([idx.strftime('%m-%d') for idx in df.index], rotation=45)
    
    def _draw_volume(self, ax, df: pd.DataFrame) -> None:
        """绘制成交量"""
        width = 0.6
        
        for i in range(len(df)):
            # 判断涨跌
            if df['close'].iloc[i] >= df['open'].iloc[i]:
                color = '#ff4136'  # 红色
            else:
                color = '#2ecc40'  # 绿色
            
            ax.bar(i, df['volume'].iloc[i], width=width, color=color, alpha=0.6)
        
        ax.set_xlim(-1, len(df))
    
    def plot_with_indicators(
        self,
        data: pd.DataFrame,
        indicators: Dict[str, pd.Series],
        title: str = '技术指标图',
        save_path: str = None,
        figsize: Tuple[int, int] = (14, 10)
    ) -> None:
        """
        绘制带技术指标的图表
        
        Args:
            data: 股票数据
            indicators: 指标字典 {指标名称: 指标数据}
            title: 图表标题
            save_path: 保存路径
            figsize: 图表大小
        """
        df = data.copy()
        
        # 转换日期
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # 创建子图
        n_indicators = len(indicators)
        fig, axes = plt.subplots(n_indicators + 1, 1, figsize=figsize,
                                gridspec_kw={'height_ratios': [3] + [1]*n_indicators},
                                sharex=True)
        
        if n_indicators == 0:
            axes = [axes]
        
        # 绘制K线
        self._draw_candlesticks(axes[0], df)
        axes[0].set_title(title, fontsize=16, fontweight='bold')
        axes[0].set_ylabel('价格', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        
        # 绘制指标
        for i, (name, indicator) in enumerate(indicators.items(), 1):
            ax = axes[i]
            ax.plot(df.index, indicator, label=name, linewidth=1.5)
            ax.set_ylabel(name, fontsize=12)
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 图表已保存: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_backtest_result(
        self,
        daily_values: List[Dict],
        trades: List[Dict],
        title: str = '回测结果',
        save_path: str = None,
        figsize: Tuple[int, int] = (14, 12)
    ) -> None:
        """
        绘制回测结果
        
        Args:
            daily_values: 每日市值数据
            trades: 交易记录
            title: 图表标题
            save_path: 保存路径
            figsize: 图表大小
        """
        df = pd.DataFrame(daily_values)
        
        # 转换日期
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # 创建子图
        fig, axes = plt.subplots(3, 1, figsize=figsize,
                                gridspec_kw={'height_ratios': [2, 1, 1]},
                                sharex=True)
        
        # 1. 资金曲线
        ax1 = axes[0]
        ax1.plot(df.index, df['total_value'], label='总市值', 
                color='blue', linewidth=2)
        ax1.axhline(y=df['total_value'].iloc[0], color='gray', 
                   linestyle='--', alpha=0.5, label='初始资金')
        
        # 标记买卖点
        for trade in trades:
            date = pd.to_datetime(trade['date'])
            if date in df.index:
                if trade['type'] == 'BUY':
                    ax1.scatter(date, df.loc[date, 'total_value'], 
                               marker='^', color='red', s=100, zorder=5)
                else:
                    ax1.scatter(date, df.loc[date, 'total_value'], 
                               marker='v', color='green', s=100, zorder=5)
        
        ax1.set_title(title, fontsize=16, fontweight='bold')
        ax1.set_ylabel('市值', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. 持仓数量
        ax2 = axes[1]
        ax2.fill_between(df.index, df['position'], alpha=0.3, color='blue')
        ax2.plot(df.index, df['position'], color='blue', linewidth=1.5)
        ax2.set_ylabel('持仓数量', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 3. 现金
        ax3 = axes[2]
        ax3.plot(df.index, df['cash'], label='现金', 
                color='orange', linewidth=2)
        ax3.set_ylabel('现金', fontsize=12)
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3)
        
        # 添加图例说明
        legend_elements = [
            Line2D([0], [0], marker='^', color='w', markerfacecolor='red', 
                  markersize=10, label='买入'),
            Line2D([0], [0], marker='v', color='w', markerfacecolor='green', 
                  markersize=10, label='卖出')
        ]
        ax1.legend(handles=legend_elements, loc='upper right')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 回测结果图已保存: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_strategy_comparison(
        self,
        results: List[Dict[str, Any]],
        title: str = '策略对比',
        save_path: str = None,
        figsize: Tuple[int, int] = (12, 6)
    ) -> None:
        """
        绘制策略对比图
        
        Args:
            results: 策略结果列表
            title: 图表标题
            save_path: 保存路径
            figsize: 图表大小
        """
        # 提取数据
        strategies = [r['strategy'] for r in results]
        returns = [r['return'] * 100 for r in results]
        sharpes = [r['sharpe'] for r in results]
        drawdowns = [r['drawdown'] * 100 for r in results]
        
        # 创建图表
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        # 1. 收益率对比
        axes[0].bar(strategies, returns, color=['green' if r > 0 else 'red' for r in returns])
        axes[0].set_title('收益率对比', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('收益率 (%)', fontsize=12)
        axes[0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # 2. 夏普比率对比
        axes[1].bar(strategies, sharpes, color='blue')
        axes[1].set_title('夏普比率对比', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('夏普比率', fontsize=12)
        axes[1].axhline(y=1, color='green', linestyle='--', alpha=0.5, label='良好')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis='y')
        
        # 3. 最大回撤对比
        axes[2].bar(strategies, drawdowns, color='red')
        axes[2].set_title('最大回撤对比', fontsize=14, fontweight='bold')
        axes[2].set_ylabel('最大回撤 (%)', fontsize=12)
        axes[2].grid(True, alpha=0.3, axis='y')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 策略对比图已保存: {save_path}")
        else:
            plt.show()
        
        plt.close()


# 导出类
__all__ = ['ChartGenerator']
