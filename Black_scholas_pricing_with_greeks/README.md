## Black-Scholes Option Pricing & Greeks Calculator

This project computes **Black-Scholes prices** for European call and put options, along with key **Greeks** (Delta, Gamma, Vega, Theta, Rho) for given trading days and exports the results to an Excel file.

## Why Black-Scholes?

The **Black-Scholes model** is a foundational model in quantitative finance, used to estimate the fair price of European options. It's widely used due to its closed-form solution, interpretability, and role as a benchmark for more advanced models.

##  What This Script Does

- Takes in a list of option parameters (spot price, strike, time to maturity, volatility, risk-free rate, etc.)
- Calculates:
  - Call and Put prices using the Black-Scholes formula
  - Greeks: Delta, Gamma, Vega, Theta, Rho
- Saves the output neatly into an Excel file for analysis/reporting

##  Tech Stack

- Python
- `numpy`, `scipy`, `pandas`
- `openpyxl` for Excel export

## Output

The output Excel contains the following columns for each option and date:
- Spot Price, Strike Price, Maturity, Volatility, Risk-Free Rate
- Call Price, Put Price
- Delta, Gamma, Vega, Theta, Rho (for both call and put)

---

This project is part of a larger personal quant toolkit aimed at implementing, testing, and understanding option pricing models and strategies.
