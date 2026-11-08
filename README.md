# Vectorized Momentum Backtesting Engine

An exploration of algorithmic momentum strategies in highly liquid US equity markets. This project constructs an end-to-end vectorized backtesting engine for **SPY**, testing the statistical validity of moving average crossovers while accounting for execution latency.

## Quantitative Methodology

### Data Ingestion
The pipeline utilizes programmatic retrieval of historical market data via `yfinance`. It downloads daily historical adjusted closing prices to natively account for corporate actions, stock splits, and dividend distributions, avoiding artificial price gaps.

### Signal Generation Logic
The engine isolates trend-following alpha by tracking short-term price velocity against an institutional baseline trend:
* **Short-Term Trend Vector**: 20-day Simple Moving Average (SMA)
* **Long-Term Trend Vector**: 50-day Simple Moving Average (SMA)
* **Position Vector**: Went long (1) when SMA₂₀ > SMA₅₀, otherwise shifted to cash (0).

### Institutional Risk & Friction Mitigations
* **Lookahead Bias Control**: A mandatory one-day latency lag (`.shift(1)`) is embedded into the execution positions. This ensures trades occur at the market open *following* a signal calculation, eliminating non-causal future information leakage.
* **Vectorized Execution**: Returns are calculated in log-space to ensure time-additivity and computational scaling efficiency during backtesting.
