# Implied Volatility Forecasting using Inverse Black-Scholes

This project estimates **Implied Volatility (IV)** from market option prices using the **inverse of the Black-Scholes model**, and tracks how IV evolves over time for forecasting and strategy design.

##  Why Implied Volatility?

While historical volatility looks backward, **Implied Volatility reflects market expectations** of future volatility. Extracting IV from option prices gives insight into how the market is pricing risk — a crucial input for:

- Option trading strategies
- Volatility forecasting
- Risk management

## What This Code Does

- Takes in market option prices (calls or puts), along with strike, spot price, maturity, and risk-free rate
- Uses numerical methods (e.g., Newton-Raphson or Brent's method) to **invert the Black-Scholes formula** and solve for implied volatility
- Outputs IV for different options across dates to Excel

##  Tech Stack

- Python
- `scipy.optimize` for root finding
- `pandas`, `numpy`
- `openpyxl` for Excel export

##  Output

An Excel file containing:
- Input parameters (Spot, Strike, Maturity, Market Price, etc.)
- Computed Implied Volatility

---

