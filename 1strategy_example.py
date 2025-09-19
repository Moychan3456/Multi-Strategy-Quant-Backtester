# ============================================
# NOTE: This is a simplified demo script
# The real proprietary strategy logic is not shared.
# This file is for showcasing backtester architecture only.
# ============================================

from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# ================================
#   CONFIGURATION
# ================================
symbol = "GBP/CHF"
timeframe = "4H"
start_date = datetime(2020, 1, 1)
end_date = datetime(2025, 9, 11)

capital = 100000
risk_per_trade_pct = 0.5
risk_per_trade_dollars = capital * risk_per_trade_pct / 100
reward_ratio = 2.0

# ================================
#   DUMMY DATA GENERATION
# ================================
dates = pd.date_range(start=start_date, end=end_date, freq="4H")
prices = np.cumsum(np.random.randn(len(dates))) + 1.25
df_resampled = pd.DataFrame({
    "Open": prices + np.random.randn(len(dates))*0.001,
    "High": prices + np.random.rand(len(dates))*0.002,
    "Low": prices - np.random.rand(len(dates))*0.002,
    "Close": prices + np.random.randn(len(dates))*0.001
}, index=dates)

# ================================
#   STRATEGY 1 (simple bullish pattern)
# ================================
def strategy1(df):
    trades = []
    for i in range(2, len(df)-1):
        c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        if c1.Close > c1.Open and c2.Close > c2.Open:
            entry_price = c3.Open
            stop_loss = min(c1.Low, c2.Low)
            target = entry_price + reward_ratio * (entry_price - stop_loss)
            pnl = (target - entry_price)
            trades.append({"Strategy":"S1","EntryTime":c3.name,"ExitTime":c3.name,"EntryPrice":entry_price,"ExitPrice":target,"PnL_Dollars":pnl*1000})
    return trades

# ================================
#   STRATEGY 2 (simple bearish pattern)
# ================================
def strategy2(df):
    trades = []
    for i in range(2, len(df)-1):
        c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        if c1.Close < c1.Open and c2.Close < c2.Open:
            entry_price = c3.Open
            stop_loss = max(c1.High, c2.High)
            target = entry_price - reward_ratio * (stop_loss - entry_price)
            pnl = (entry_price - target)
            trades.append({"Strategy":"S2","EntryTime":c3.name,"ExitTime":c3.name,"EntryPrice":entry_price,"ExitPrice":target,"PnL_Dollars":pnl*1000})
    return trades

# ================================
#   STRATEGY 3 (random breakout)
# ================================
def strategy3(df):
    trades = []
    for i in range(5, len(df)-1):
        window = df.iloc[i-5:i]
        if df.iloc[i].Close > window.High.max():
            entry_price = df.iloc[i+1].Open
            stop_loss = window.Low.min()
            target = entry_price + reward_ratio * (entry_price - stop_loss)
            pnl = (target - entry_price)
            trades.append({"Strategy":"S3","EntryTime":df.index[i+1],"ExitTime":df.index[i+1],"EntryPrice":entry_price,"ExitPrice":target,"PnL_Dollars":pnl*1000})
    return trades

# ================================
#   RUN STRATEGIES
# ================================
trades = strategy1(df_resampled) + strategy2(df_resampled) + strategy3(df_resampled)
all_trades = pd.DataFrame(trades)

if not all_trades.empty:
    all_trades.set_index("ExitTime", inplace=True)
    all_trades["CumulativePnL"] = all_trades["PnL_Dollars"].cumsum()
    all_trades["Capital"] = capital + all_trades["CumulativePnL"]

    # Performance metrics
    equity_curve = all_trades["Capital"]
    daily_equity = equity_curve.resample("D").ffill()
    daily_returns = daily_equity.pct_change().dropna()
    mean_daily, std_daily = daily_returns.mean(), daily_returns.std()
    sharpe = (mean_daily/std_daily)*math.sqrt(252) if std_daily!=0 else np.nan
    downside = daily_returns[daily_returns<0].std()
    sortino = (mean_daily/downside)*math.sqrt(252) if downside!=0 else np.nan
    total_days = (all_trades.index[-1]-all_trades.index[0]).days
    final_cap = equity_curve.iloc[-1]
    cagr = (final_cap/capital)**(365/total_days)-1 if total_days>0 else np.nan
    rolling_max = equity_curve.cummax()
    drawdown = equity_curve/rolling_max - 1
    max_dd = drawdown.min()
    calmar = cagr/abs(max_dd) if max_dd!=0 else np.nan

    print("========== COMBINED STRATEGY PERFORMANCE ==========")
    print(f"Initial Capital: ${capital:,.2f}")
    print(f"Final Capital:   ${final_cap:,.2f}")
    print(f"Total Trades:    {len(all_trades)}")
    print(f"Sharpe Ratio:    {sharpe:.2f}")
    print(f"Sortino Ratio:   {sortino:.2f}")
    print(f"Calmar Ratio:    {calmar:.2f}")
    print(f"Max Drawdown:    {max_dd*100:.2f}%")

    # Plots
    fig, ax = plt.subplots(2,1,figsize=(12,6),sharex=True)
    equity_curve.plot(ax=ax[0],label="Equity Curve",color="blue")
    ax[0].set_title("Equity Curve")
    ax[0].legend()
    drawdown.plot(ax=ax[1],color="red")
    ax[1].set_title("Drawdown")
    plt.tight_layout()
    plt.show()
