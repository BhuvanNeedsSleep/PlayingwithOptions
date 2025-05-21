# GARCH(1,1) Volatility Forecasting on SPX

This project implements a **GARCH(1,1)** model to forecast daily volatility of the **S&P 500 Index (SPX)** based on historical returns.

##  Why GARCH?

GARCH models (Generalized Autoregressive Conditional Heteroskedasticity) are widely used in finance to:

- Capture **volatility clustering** observed in financial returns
- Forecast **conditional volatility** dynamically over time
- Improve **risk management**, option pricing, and trading strategies

## What This Code Does

The GARCH(1,1) model forecasts implied volatility (IV) by modeling its time-series variance, capturing volatility clustering in financial markets. This code applies GARCH(1,1) to SPXW call option IVs derived from 1-minute SPX/SPXW data via Inverse Black-Scholes. It filters for valid option prices (>0) and time to expiration (7-60 days), fits the model to daily ATM IVs across multiple trading days (May 15–31, 2024), and forecasts future IV with confidence intervals. Results are visualized and exported to Excel, demonstrating advanced volatility modeling and time-series analysis.

## Tech Stack

- Python
- `arch` (for GARCH modeling)
- `pandas`, `numpy`, `matplotlib`

## Input

- Historical SPX prices in CSV format with columns: `Date`, `Close`

---

