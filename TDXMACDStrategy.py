import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from client.quotationClient import QuotationClient
from const import MARKET, PERIOD

class TDXMACDStrategy:
    def __init__(self, market, code):
        self.market = market
        self.code = code
        self.client = QuotationClient()
        success = self.client.connect().login(show_info=True)
        if success:
            print("登录成功")
        else:
            print("登录失败")
        self.data = None
        self.signals = None
        self.portfolio = None

    def fetch_data(self):
        """获取股票K线数据"""
        try:
            print(f"正在获取 {self.code} 的K线数据...")
            print(f"市场: {self.market}, 代码: {self.code}, 周期: PERIOD.DAILY")

            # 获取日线数据 (PERIOD.DAILY)
            self.data = self.client.get_KLine_data(
                market=self.market,
                code=self.code,
                period=PERIOD.DAILY,
                start=0,
                count=800
            )

            if not self.data:
                print(f"获取 {self.code} 的数据失败，返回空数据")
                return False

            # 转换为DataFrame
            df = pd.DataFrame(self.data)

            print(f"DataFrame列: {df.columns.tolist()}")
            # 设置日期为索引
            df.set_index('datetime', inplace=True)

            # 确保必要的列存在
            required_columns = ['open', 'high', 'low', 'close', 'vol', 'amount']
            for col in required_columns:
                if col not in df.columns:
                    print(f"缺少必要的列: {col}")
                    return False

            self.data = df
            print(f"成功获取 {self.code} 的数据，共 {len(self.data)} 条记录")
            return True

        except Exception as e:
            print(f"获取数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def calculate_macd(self, fast_period=12, slow_period=26, signal_period=9):
        """计算MACD指标"""
        if self.data is None:
            print("请先获取数据")
            return

        # 计算EMA
        ema_fast = self.data['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = self.data['close'].ewm(span=slow_period, adjust=False).mean()

        # 计算MACD线
        macd_line = ema_fast - ema_slow

        # 计算信号线
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

        # 计算MACD柱状图
        macd_hist = macd_line - signal_line

        # 添加到数据中
        self.data['MACD_Line'] = macd_line
        self.data['Signal_Line'] = signal_line
        self.data['MACD_Hist'] = macd_hist

    def generate_signals(self):
        """生成交易信号"""
        if 'MACD_Line' not in self.data.columns:
            print("请先计算MACD指标")
            return

        self.signals = pd.DataFrame(index=self.data.index)
        self.signals['price'] = self.data['close']
        self.signals['signal'] = 0

        # 金叉信号：MACD线上穿信号线且MACD柱状图由负转正
        self.signals.loc[((self.data['MACD_Line'] > self.data['Signal_Line']) &
                         (self.data['MACD_Line'].shift(1) <= self.data['Signal_Line'].shift(1)) &
                         (self.data['MACD_Hist'] > 0) &
                         (self.data['MACD_Hist'].shift(1) <= 0)), 'signal'] = 1

        # 死叉信号：MACD线下穿信号线且MACD柱状图由正转负
        self.signals.loc[((self.data['MACD_Line'] < self.data['Signal_Line']) &
                         (self.data['MACD_Line'].shift(1) >= self.data['Signal_Line'].shift(1)) &
                         (self.data['MACD_Hist'] < 0) &
                         (self.data['MACD_Hist'].shift(1) >= 0)), 'signal'] = -1

    def backtest(self, initial_capital=10000, position_size=0.1):
        """回测策略"""
        if self.signals is None:
            print("请先生成交易信号")
            return

        self.portfolio = pd.DataFrame(index=self.signals.index)
        self.portfolio['price'] = self.signals['price']
        self.portfolio['signal'] = self.signals['signal']
        self.portfolio['position'] = self.signals['signal'].diff()

        # 初始化资金
        self.portfolio['cash'] = initial_capital
        self.portfolio['shares'] = 0
        self.portfolio['total'] = initial_capital

        current_position = 0
        for i in range(len(self.portfolio)):
            if i > 0:
                # 复制前一天的数据
                self.portfolio.loc[self.portfolio.index[i], 'cash'] = self.portfolio.loc[self.portfolio.index[i-1], 'cash']
                self.portfolio.loc[self.portfolio.index[i], 'shares'] = self.portfolio.loc[self.portfolio.index[i-1], 'shares']

            # 处理交易信号
            if self.portfolio.loc[self.portfolio.index[i], 'signal'] == 1 and current_position <= 0:
                # 买入
                shares_to_buy = int((self.portfolio.loc[self.portfolio.index[i], 'cash'] * position_size) /
                                  self.portfolio.loc[self.portfolio.index[i], 'price'])
                cost = shares_to_buy * self.portfolio.loc[self.portfolio.index[i], 'price']
                self.portfolio.loc[self.portfolio.index[i], 'cash'] -= cost
                self.portfolio.loc[self.portfolio.index[i], 'shares'] += shares_to_buy
                current_position = 1

            elif self.portfolio.loc[self.portfolio.index[i], 'signal'] == -1 and current_position >= 0:
                # 卖出
                shares_to_sell = self.portfolio.loc[self.portfolio.index[i], 'shares']
                proceeds = shares_to_sell * self.portfolio.loc[self.portfolio.index[i], 'price']
                self.portfolio.loc[self.portfolio.index[i], 'cash'] += proceeds
                self.portfolio.loc[self.portfolio.index[i], 'shares'] = 0
                current_position = -1

            # 计算总资产
            self.portfolio.loc[self.portfolio.index[i], 'total'] = (
                self.portfolio.loc[self.portfolio.index[i], 'cash'] +
                self.portfolio.loc[self.portfolio.index[i], 'shares'] *
                self.portfolio.loc[self.portfolio.index[i], 'price']
            )

    def calculate_metrics(self):
        """计算回测指标"""
        if self.portfolio is None:
            print("请先进行回测")
            return

        metrics = {}

        # 总收益率
        total_return = (self.portfolio['total'].iloc[-1] / self.portfolio['total'].iloc[0] - 1) * 100
        metrics['总收益率'] = f"{total_return:.2f}%"

        # 年化收益率
        days = (self.portfolio.index[-1] - self.portfolio.index[0]).days
        if days > 0:
            annual_return = ((1 + total_return/100) ** (365/days) - 1) * 100
            metrics['年化收益率'] = f"{annual_return:.2f}%"
        else:
            metrics['年化收益率'] = "0.00%"

        # 最大回撤
        self.portfolio['cum_max'] = self.portfolio['total'].cummax()
        self.portfolio['drawdown'] = (self.portfolio['total'] / self.portfolio['cum_max'] - 1) * 100
        max_drawdown = self.portfolio['drawdown'].min()
        metrics['最大回撤'] = f"{max_drawdown:.2f}%"

        # 夏普比率（假设无风险利率为3%）
        daily_returns = self.portfolio['total'].pct_change()
        if len(daily_returns.dropna()) > 0:
            sharpe_ratio = (daily_returns.mean() - 0.03/252) / (daily_returns.std()) * np.sqrt(252)
            metrics['夏普比率'] = f"{sharpe_ratio:.2f}"
        else:
            metrics['夏普比率'] = "0.00"

        # 交易次数
        trade_count = len(self.portfolio[self.portfolio['position'] != 0])
        metrics['交易次数'] = trade_count

        # 胜率
        win_trades = 0
        for i in range(1, len(self.portfolio)):
            if self.portfolio['position'].iloc[i] == -1:  # 卖出信号
                entry_price = self.portfolio['price'].iloc[i-1]
                exit_price = self.portfolio['price'].iloc[i]
                if exit_price > entry_price:
                    win_trades += 1

        if trade_count > 0:
            win_rate = (win_trades / (trade_count/2)) * 100
            metrics['胜率'] = f"{win_rate:.2f}%"
        else:
            metrics['胜率'] = "0.00%"

        return metrics

    def plot_results(self):
        """绘制回测结果"""
        if self.portfolio is None:
            print("请先进行回测")
            return

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12), sharex=True)

        # 价格和交易信号
        ax1.plot(self.data.index, self.data['close'], label='价格', color='blue')
        buy_signals = self.signals[self.signals['signal'] == 1]
        sell_signals = self.signals[self.signals['signal'] == -1]
        ax1.scatter(buy_signals.index, buy_signals['price'], marker='^', color='green', label='买入信号')
        ax1.scatter(sell_signals.index, sell_signals['price'], marker='v', color='red', label='卖出信号')
        ax1.set_title(f'{self.code} MACD策略回测')
        ax1.set_ylabel('价格')
        ax1.legend()

        # MACD指标
        ax2.plot(self.data.index, self.data['MACD_Line'], label='MACD线', color='blue')
        ax2.plot(self.data.index, self.data['Signal_Line'], label='信号线', color='red')
        ax2.bar(self.data.index, self.data['MACD_Hist'], label='MACD柱状图', color='gray', alpha=0.5)
        ax2.set_ylabel('MACD')
        ax2.legend()

        # 账户价值
        ax3.plot(self.portfolio.index, self.portfolio['total'], label='账户价值', color='purple')
        ax3.set_ylabel('账户价值')
        ax3.set_xlabel('日期')
        ax3.legend()

        plt.tight_layout()
        plt.show()

    def run_full_backtest(self, initial_capital=10000, position_size=0.1):
        if not self.fetch_data():
            return

        self.calculate_macd()
        self.generate_signals()
        self.backtest(initial_capital, position_size)

        metrics = self.calculate_metrics()
        print("\n回测指标:")
        for key, value in metrics.items():
            print(f"{key}: {value}")

        self.plot_results()

# 示例使用
if __name__ == "__main__":
    # 创建并运行策略
    strategy = TDXMACDStrategy(MARKET.SZ, "002131")
    strategy.run_full_backtest(initial_capital=10000, position_size=0.1)
