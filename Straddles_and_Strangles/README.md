# Options Strategies: Straddles & Strangles with Volatility Filters

This project implements the logic for **Long Straddle** and **Long Strangle** strategies in options, with added **volatility-based entry/exit filters** to refine the setup.

##  Why Straddles & Strangles?

These are classic **non-directional strategies** designed to profit from significant moves in either direction. They are widely used when:
- The trader expects high volatility
- Direction is uncertain but magnitude matters (e.g., around earnings, major news)

## What This Code Does

- Implements:
  - **Long Straddle**: Buy ATM Call + ATM Put
  - **Long Strangle**: Buy OTM Call + OTM Put
- Adds **volatility filters** to control:
  - Entry: Enter trade only when implied/historical volatility exceeds a threshold
  - Exit: Optional rule-based exit 
- Code is modular and ready for plugging into data or backtesting pipelines

## Notes

- This code, it focuses purely on **strategy logic** and **entry/exit condition setup**
- Designed to be easy to integrate with historical or live market data
- Filters can be adjusted based on trading hypothesis

## Tech Stack

- Python
- `pandas`, `numpy`
- Logic written in function-based format for reuse

---


