# Playing With Options

A research + simulation playground for analyzing SPX index options strategies (straddle, strangle, etc.) using intraday OHLCV data.

## What This Project Does

- Fetches SPX Index + Options OHLCV data using `fetchData.py`
- Merges SPX + Call + Put data for a chosen strike & expiry
- Supports ATM auto-detection
- Handles multiple trading days
- Exports clean Excel files for further analysis

## Strategies in Scope
- We'll start with Straddles and strangles, i have a long list(15+) of
  already well known strategies, that we'll explore during first phase of
  this project.

## Files

- `export_spx_and_options.py`: Main script to fetch & export
- `fetchData.py`: Your database access logic
- `config.ini`: Credentials/configs

## To-Do

- Backtest different strike combinations
- Add Greeks & IV tracking
- Build strategy visualizer dashboard
