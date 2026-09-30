
Simple SMA Crossover Quantitative Backtest Engine
Time to deploy: < 5 minutes
import yfinance as yf
import pandas as pd
import numpy as np

def run_backtest(ticker="SPY", start_date="2023-01-01", end_date="2026-01-01"):
    print(f"Fetching historical data for {ticker}...")
    # 1. Downloading market data
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        print("No data retrieved. Check ticker or internet connection.")
        return
        
    # Flattening columns if multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 2. Defining Technical Indicators
    df['SMA_Fast'] = df['Close'].rolling(window=20).mean()
    df['SMA_Slow'] = df['Close'].rolling(window=50).mean()

    # 3. Signaling Generation (1 = Long, 0 = Cash)
    df['Signal'] = np.where(df['SMA_Fast'] > df['SMA_Slow'], 1, 0)
    
    # Shifting signals by 1 day to execute on the NEXT open/close (prevents lookahead bias)
    df['Position'] = df['Signal'].shift(1)

    # 4. Calculating Returns
    df['Market_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    df['Strategy_Returns'] = df['Market_Returns'] * df['Position']

    # 5. Performance Metrics
    cum_market = np.exp(df['Market_Returns'].cumsum()) - 1
    cum_strategy = np.exp(df['Strategy_Returns'].cumsum()) - 1

    print("\n--- BACKTEST RESULTS ---")
    print(f"Final Benchmark Return: {cum_market.iloc[-1]*100:.2f}%")
    print(f"Final Strategy Return:  {cum_strategy.iloc[-1]*100:.2f}%")
    
    return df

if __name__ == "__main__":
    # Run strategy on SPY ETF
    data = run_backtest(ticker="SPY")
