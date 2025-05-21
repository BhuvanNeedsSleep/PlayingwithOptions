# Gamma Scalping Strategy Logic

This project implements the core logic for **Gamma Scalping** a delta-neutral options strategy used to profit from volatility by dynamically hedging delta exposure.

##  What is Gamma Scalping?

Gamma scalping involves:
- Holding a **long gamma** position 
- Frequently rebalancing the **delta** using the underlying asset
- Profiting from large moves or frequent oscillations around the strike

It turns market volatility into profit, especially when actual movement exceeds implied expectations.

##  What This Code Does

- Simulates the hedging process for a long gamma position
- Rebalances delta as the underlying moves
- Tracks P&L from gamma exposure and hedging cost
- Does **not include backtesting** on real data — focuses on mechanics

## Tech Stack

- Python
- `numpy`, `pandas` for calculations

---

