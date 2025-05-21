import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
import matplotlib.pyplot as plt
from fetchData import fetchDataIndex, fetchDataOptions
import datetime

# Black-Scholes price function
def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    """Calculate Black-Scholes option price."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return price

# Inverse Black-Scholes to find IV
def implied_volatility(S, K, T, r, market_price, option_type="call", tol=1e-6):
    """Solve for IV using Brent's method."""
    def objective(sigma):
        return black_scholes_price(S, K, T, r, sigma, option_type) - market_price
    
    try:
        # Bound IV between 1% and 200%
        iv = brentq(objective, 0.01, 2.0, xtol=tol)
        return iv
    except ValueError:
        return np.nan  # Return NaN if no solution found

# Fetch and process SPX/SPXW data
def fetch_and_calculate_iv(trading_days, expiry_day, strike=None, r=0.02):
    """Fetch SPX/SPXW data and calculate IV for ATM options."""
    iv_data = []
    
    for day in trading_days:
        print(f"Processing {day}")
        # Fetch SPX data
        try:
            spx_df = fetchDataIndex("SPX", day, day).reset_index()
        except Exception as e:
            print(f"SPX fetch error on {day}: {e}")
            continue
        
        # Determine ATM strike
        S = spx_df.loc[0, "Open"]  # Use open price
        if strike is None:
            strike = round(S / 50) * 50  # Nearest 50-point strike
        
        # Time to expiration
        T = (pd.to_datetime(expiry_day) - pd.to_datetime(day)).days / 365
        
        # Fetch option data
        try:
            ce_df = fetchDataOptions("SPXW", day, day, strike, expiry_day, "CE").reset_index()
            pe_df = fetchDataOptions("SPXW", day, day, strike, expiry_day, "PE").reset_index()
        except Exception as e:
            print(f"Option fetch error on {day}: {e}")
            continue
        
        # Use first minute's option prices (open)
        call_price = ce_df.loc[0, "Open"] if not ce_df.empty else np.nan
        put_price = pe_df.loc[0, "Open"] if not pe_df.empty else np.nan
        
        # Calculate IV
        call_iv = implied_volatility(S, strike, T, r, call_price, "call") if not np.isnan(call_price) else np.nan
        put_iv = implied_volatility(S, strike, T, r, put_price, "put") if not np.isnan(put_price) else np.nan
        
        iv_data.append({
            "Date": day,
            "SPX_Open": S,
            "Strike": strike,
            "Call_IV": call_iv * 100,  # Convert to percentage
            "Put_IV": put_iv * 100,
            "Time_to_Expiry": T
        })
    
    return pd.DataFrame(iv_data)

# Forecast IV using EMA
def forecast_iv(iv_df, span=5):
    """Apply EMA to forecast IV for calls and puts."""
    iv_df["Call_IV_EMA"] = iv_df["Call_IV"].ewm(span=span, adjust=False).mean()
    iv_df["Put_IV_EMA"] = iv_df["Put_IV"].ewm(span=span, adjust=False).mean()
    return iv_df

# Main execution
if __name__ == "__main__":
    # Define trading days and expiry
    expiry_day = datetime.date(2024, 5, 31)
    trading_days = [
        datetime.date(2024, 5, 15), datetime.date(2024, 5, 16), datetime.date(2024, 5, 17),
        datetime.date(2024, 5, 20), datetime.date(2024, 5, 21), datetime.date(2024, 5, 22),
        datetime.date(2024, 5, 23), datetime.date(2024, 5, 24), datetime.date(2024, 5, 27),
        datetime.date(2024, 5, 28), datetime.date(2024, 5, 29), datetime.date(2024, 5, 30),
        datetime.date(2024, 5, 31)
    ]
    
    # Fetch and calculate IV
    iv_df = fetch_and_calculate_iv(trading_days, expiry_day)
    
    if iv_df.empty:
        print("No IV data calculated. Check fetch errors.")
    else:
        # Forecast IV
        iv_df = forecast_iv(iv_df, span=5)
        
        # Export to Excel
        iv_df.to_excel("spxw_iv_forecast.xlsx", index=False)
        print("IV data exported to spxw_iv_forecast.xlsx")
        
        # Visualize IV trends
        plt.figure(figsize=(12, 6))
        plt.plot(iv_df["Date"], iv_df["Call_IV"], label="Call IV (%)", marker="o")
        plt.plot(iv_df["Date"], iv_df["Put_IV"], label="Put IV (%)", marker="s")
        plt.plot(iv_df["Date"], iv_df["Call_IV_EMA"], label="Call IV EMA", linestyle="--")
        plt.plot(iv_df["Date"], iv_df["Put_IV_EMA"], label="Put IV EMA", linestyle="--")
        plt.title("SPXW ATM Implied Volatility and EMA Forecast (May 2024)")
        plt.xlabel("Date")
        plt.ylabel("Implied Volatility (%)")
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("iv_forecast_plot.png")
        plt.show()