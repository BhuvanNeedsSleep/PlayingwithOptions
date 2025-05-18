## Options strategy Engine

A full-fledged research + backtesting + simulation engine for building, analyzing, and deploying volatility-driven options strategies — built from scratch using real market data.
 
 We'll Build using:
- SPX & SPXW options data (minute-level)
- Volatility modeling (IV, Greeks, BS, stochastic/local vol, etc.)
- Strategy logic coded in Python
- Realistic filters (IV rank, volume, expiry distance)
- Jupyter notebooks + Excel outputs for visual analysis

## 🎯 Project Goals

- Implement well-known options strategies
- Apply correct strategy in the right volatility regime
- Backtest for different DTEs, strikes, IV conditions
- Analyze PnL, Greeks, IV movement, liquidity
- Build trading intuition through live simulations and paper trades

## -:Strategy Roadmap:-
1) DATA FORMATION
   - Extract data from spx, spxw
   - Export the data into excel sheets for better visualization
   - Filtering the liquid data, Drop NaNs(1m data is illquid unless there's news, near-to expiry, so we'll use 5m, 15m or 1d data)
     
2) Enhance with Bs pricing/ Greeks
   - Calculate Bs prices call/put
   - calculate option greeks
   - Estimate IV by inverse BS
   - Add them to our excel data.
     
 3) Implement Strategies
    - Apply/Backtest one strategy at a time. Understand it thoroughly, understand its edge and risk
      
 4) Plot+ Evaluate the performance
    - Calculate PnL over time.
    - Daily Pnl
    - Max drawdown
    - Sharpe ratio/ Sortino ratio
    - PnL vs IV/vega/theta
      
  5) Add Smart entry/exit conditions, IV rank filters.
  
  6) Paper-Trading in Platforms like TradingView, Optionstrats, Sensibull

So, First lets implement well known strategies, Here's the list of Strategies we'll be trying out:-
1) Straddles, Strangles
2) Calender spread, vertical spread, Diagonal spread
3) Iron condors, Super condors Strategy
4) Gamma scalping
5) IV crush, Skew, Surface, Smiles
6) Protective collar/ Rolling puts
7) Delta- Neutral earning
8) RSI 2.0 Bull put ladder
9) Volatility skew Arbitrage
10) Broken wing Butterfly

##  Models and Methods Used

| Model / Concept | Usage |
|-----------------|-------|
| **Black-Scholes** | Pricing + Greeks |
| **IV Estimation** | Reverse-engineered from market data |
| **GARCH(1,1)** | Forecasting volatility time-series |
| **Jump-Diffusion (Merton)** | Captures unexpected big moves |
| **Heston Model** | For stochastic volatility simulation |
| **Greeks (Delta, Gamma, Theta, Vega)** | Risk + behavior understanding |
| **IV Rank & IV Percentile** | Entry filters |
| **Liquidity filters** | Avoid NaN/illiquid data points |
| **Local Volatality Model** | Dupire's eqn |
     
      

     
         
            
      
