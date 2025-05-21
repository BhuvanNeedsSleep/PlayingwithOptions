# IV Smile, Skew, and Surface Visualization

This codes focuses on visualizing **Implied Volatility (IV) structures** from option market data — including **IV Smile**, **IV Skew**, and **IV Surface** — to understand how volatility varies with strike and maturity.

##  Why IV Structures Matter

Implied volatility is not constant across strikes and expiries. Observing its shape helps:

- Detect **market sentiment**
- Identify **mispriced options**
- Improve **volatility modeling** and **strategy selection**

##  What This Code Does

- **IV Smile**: Plots IV vs Strike for a fixed expiry
- **IV Skew**: Plots IV vs Delta or moneyness
- **IV Surface**: 3D plot of IV vs Strike and Expiry
- Accepts option chain data (strike, expiry, IV)
- Built for fast and intuitive visual diagnostics

##  Tech Stack

- Python
- `matplotlib`, `plotly` or `mpl_toolkits` (for 3D surfaces)
- `pandas`, `numpy`



---


