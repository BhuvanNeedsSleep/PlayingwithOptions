# Options Strategies: Calendar, Vertical, and Diagonal Spreads

This code implements the core logic for **Calendar**, **Vertical**, and **Diagonal Spread** strategies foundational tools in multi-leg options trading. Each strategy is designed for specific volatility and directional outlooks, and includes **basic filters** to enhance setup quality.



## What This Code Does

- Implements:
  - **Vertical Spreads**: Buy/Sell options of same expiry, different strikes (Bull Call, Bear Put)
  - **Calendar Spreads**: Buy longer-dated option, sell shorter-dated option (same strike)
  - **Diagonal Spreads**: Combination of both — different strike and expiry
- Includes **basic filters** like:
  - IV environment checks (enter only in low/high IV setups)
  - Optional rules to select strikes based on delta or moneyness
- No backtesting — logic only, structured for integration into broader backtesting frameworks

##  Notes

- Emphasis is on **strategy logic** and **trade setup structure**
- Can be extended easily for historical testing or live implementation
- Useful for building modular options strategy libraries

##  Tech Stack

- Python
- `pandas`, `numpy`
- Strategy logic structured as reusable functions

---

