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
        iv = brentq(objective, 0.01, 2.0, xtol=tol)
        return iv
    except ValueError:
        return np.nan

# Fetch and calculate volatility smile
def calculate_volatility_smile(trading_day, expiry_day, strikes, r=0.02):
    """Calculate IV for multiple strikes to form a volatility smile."""
    # Fetch SPX data
    try:
        spx_df = fetchDataIndex("SPX", trading_day, trading_day).reset_index()
        S = spx_df.loc[0, "Open"]  # Use first minute's open
    except Exception as e:
        print(f"SPX fetch error on {trading_day}: {e}")
        return None
    
    # Time to expiration
    T = (pd.to_datetime(expiry_day) - pd.to_datetime(trading_day)).days / 365
    
    # Filter: Ensure T is 7-60 days
    if not (7 <= T * 365 <= 60):
        print(f"Time to expiry ({T*365:.0f} days) outside [7, 60]")
        return None
    
    smile_data = []
    for strike in strikes:
        # Fetch call and put data
        try:
            ce_df = fetchDataOptions("SPXW", trading_day, trading_day, strike, expiry_day, "CE").reset_index()
            pe_df = fetchDataOptions("SPXW", trading_day, trading_day, strike, expiry_day, "PE").reset_index()
        except Exception as e:
            print(f"Option fetch error for strike {strike}: {e}")
            continue
        
        # Use first minute's open price
        call_price = ce_df.loc[0, "Open"] if not ce_df.empty else np.nan
        put_price = pe_df.loc[0, "Open"] if not pe_df.empty else np.nan
        
        # Filter: Ensure prices are positive
        if np.isnan(call_price) or call_price <= 0 or np.isnan(put_price) or put_price <= 0:
            print(f"Invalid prices for strike {strike}: Call=${call_price}, Put=${put_price}")
            continue
        
        # Calculate IV
        call_iv = implied_volatility(S, strike, T, r, call_price, "call")
        put_iv = implied_volatility(S, strike, T, r, put_price, "put")
        
        smile_data.append({
            "Strike": strike,
            "Call_IV": call_iv * 100 if not np.isnan(call_iv) else np.nan,
            "Put_IV": put_iv * 100 if not np.isnan(put_iv) else np.nan
        })
    
    return pd.DataFrame(smile_data)

# Main execution
if __name__ == "__main__":
    trading_day = datetime.date(2024, 5, 15)
    expiry_day = datetime.date(2024, 5, 31)
    
    # Define strikes (±200 points from ATM, step=50)
    spx_df = fetchDataIndex("SPX", trading_day, trading_day).reset_index()
    S = spx_df.loc[0, "Open"]
    atm_strike = round(S / 50) * 50
    strikes = np.arange(atm_strike - 200, atm_strike + 201, 50)
    
    # Calculate volatility smile
    smile_df = calculate_volatility_smile(trading_day, expiry_day, strikes)
    
    if smile_df is None or smile_df.empty:
        print("No valid smile data calculated.")
    else:
        # Export to Excel
        smile_df.to_excel("spxw_volatility_smile.xlsx", index=False)
        print("Smile data exported to spxw_volatility_smile.xlsx")
        
        # Visualize smile
        plt.figure(figsize=(10, 6))
        plt.plot(smile_df["Strike"], smile_df["Call_IV"], marker="o", label="Call IV")
        plt.plot(smile_df["Strike"], smile_df["Put_IV"], marker="s", label="Put IV")
        plt.axvline(atm_strike, color="k", linestyle="--", label="ATM Strike")
        plt.title(f"SPXW Volatility Smile ({trading_day}, Expiry: {expiry_day})")
        plt.xlabel("Strike Price ($)")
        plt.ylabel("Implied Volatility (%)")
        plt.legend()
        plt.grid()
        plt.savefig("volatility_smile.png")
        plt.show()