# Options Strategy: Iron Condor with Entry Filters

This project implements the **Iron Condor** options strategy — a popular non-directional strategy used to profit from low-volatility environments — along with basic filters to enhance trade selection.

## Why Iron Condors?

The Iron Condor is ideal when:
- The trader expects the underlying to stay within a range
- There is high implied volatility that’s expected to decrease
- Risk is defined and returns are steady if price stays between breakevens

It works by combining two vertical spreads:
- **Bear Call Spread** (Sell OTM Call, Buy higher OTM Call)
- **Bull Put Spread** (Sell OTM Put, Buy lower OTM Put)

##  What This Code Does

- Implements the full Iron Condor setup with customizable:
  - Strike distances (wingspan)
  - Entry thresholds

- Does **not include backtesting** — focuses on modular strategy logic

##  Notes

- Code is structured to allow easy integration into backtesting or live trading systems
- Useful for building logic blocks for systematic options strategy engines

##  Tech Stack

- Python
- `pandas`, `numpy`


---


