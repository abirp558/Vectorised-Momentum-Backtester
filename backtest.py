
import yfinance as yf
import pandas as pd
import numpy as np

def run_backtest(ticker="SPY", start_date="2023-01-01", end_date="2026-01-01", transaction_fee=0.0005):
    print(f"Fetching historical market data for {ticker}...")
    
    # 1. Download market data
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        print("No data retrieved. Check ticker or internet connection.")
        return
        
    # Flatten columns if multi-index (compatibility for newer yfinance versions)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    # 2. Define Technical Indicators
    df['SMA_Fast'] = df['Close'].rolling(window=20).mean()
    df['SMA_Slow'] = df['Close'].rolling(window=50).mean()
    
    # 3. Signal Generation (1 = Long, 0 = Cash)
    df['Signal'] = np.where(df['SMA_Fast'] > df['SMA_Slow'], 1, 0)
    
    # Shift signals by 1 day to execute on NEXT market open/close (prevents lookahead bias)
    df['Position'] = df['Signal'].shift(1)
    
    # 4. Calculate Returns & Implement Transaction Costs
    df['Market_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Identify trade execution triggers (1 or -1 when position changes)
    df['Trades'] = df['Position'].diff().fillna(0).abs()
    
    # Subtract a fixed fee percentage (e.g., 0.05%) for every trade executed
    df['Strategy_Returns'] = (df['Market_Returns'] * df['Position']) - (df['Trades'] * transaction_fee)
    
    # Drop NaNs resulting from indicators and lookback shifts
    df = df.dropna()

    # 5. Advanced Performance & Risk Metrics
    cum_market = np.exp(df['Market_Returns'].cumsum()) - 1
    cum_strategy = np.exp(df['Strategy_Returns'].cumsum()) - 1
    
    # Annualized Sharpe Ratio (Assuming a 0% Risk-Free Rate baseline proxy)
    daily_strategy_mean = df['Strategy_Returns'].mean()
    daily_strategy_std = df['Strategy_Returns'].std()
    if daily_strategy_std != 0:
        sharpe_ratio = (daily_strategy_mean / daily_strategy_std) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0

    # Maximum Drawdown Calculation (Peak-to-Trough Portfolio Volatility)
    strategy_wealth_index = np.exp(df['Strategy_Returns'].cumsum())
    previous_peaks = strategy_wealth_index.cummax()
    drawdowns = (strategy_wealth_index - previous_peaks) / previous_peaks
    max_drawdown = drawdowns.min()

    # 6. Display Institutional Terminal Output
    print("\n" + "="*45)
    print(f"     BACKTEST ANALYSIS: {ticker.upper()}     ")
    print("="*45)
    print(f"Final Benchmark Return  : {cum_market.iloc[-1]*100:.2f}%")
    print(f"Final Strategy Return   : {cum_strategy.iloc[-1]*100:.2f}% (Net of Fees)")
    print(f"Annualized Sharpe Ratio : {sharpe_ratio:.2f}")
    print(f"Maximum Drawdown Risk   : {max_drawdown*100:.2f}%")
    print(f"Total Trades Executed   : {int(df['Trades'].sum())}")
    print(f"Applied Transaction Fee : {transaction_fee*100:.3f}% per trade")
    print("="*45 + "\n")
    
    return df

if __name__ == "__main__":
    # Execute default backtest pipeline on SPY
    run_backtest(ticker="SPY")
