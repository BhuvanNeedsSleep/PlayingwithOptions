import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
import plotly.graph_objects as go
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

# Fetch and calculate IV surface
def calculate_iv_surface(trading_day, expiry_days, strikes, r=0.02):
    """Calculate IV surface across strikes and expirations."""
    # Fetch SPX data
    try:
        spx_df = fetchDataIndex("SPX", trading_day, trading_day).reset_index()
        S = spx_df.loc[0, "Open"]
    except Exception as e:
        print(f"SPX fetch error on {trading_day}: {e}")
        return None
    
    surface_data = []
    for expiry_day in expiry_days:
        # Time to expiration
        T = (pd.to_datetime(expiry_day) - pd.to_datetime(trading_day)).days / 365
        
        # Filter: Ensure T is 7-180 days
        if not (7 <= T * 365 <= 180):
            print(f"Time to expiry ({T*365:.0f} days) outside [7, 180] for {expiry_day}")
            continue
        
        for strike in strikes:
            # Fetch call data (use calls for simplicity)
            try:
                ce_df = fetchDataOptions("SPXW", trading_day, trading_day, strike, expiry_day, "CE").reset_index()
            except Exception as e:
                print(f"Option fetch error for strike {strike}, expiry {expiry_day}: {e}")
                continue
            
            # Use first minute's open price
            call_price = ce_df.loc[0, "Open"] if not ce_df.empty else np.nan
            
            # Filter: Ensure price is positive
            if np.isnan(call_price) or call_price <= 0:
                print(f"Invalid call price for strike {strike}, expiry {expiry_day}: ${call_price}")
                continue
            
            # Calculate IV
            call_iv = implied_volatility(S, strike, T, r, call_price, "call")
            
            surface_data.append({
                "Strike": strike,
                "Expiry": expiry_day,
                "Days_to_Expiry": T * 365,
                "Call_IV": call_iv * 100 if not np.isnan(call_iv) else np.nan
            })
    
    return pd.DataFrame(surface_data)

# Main execution
if __name__ == "__main__":
    trading_day = datetime.date(2024, 5, 15)
    expiry_days = [
        datetime.date(2024, 5, 31),
        datetime.date(2024, 6, 28),
        datetime.date(2024, 7, 31)
    ]
    
    # Define strikes (±200 points from ATM, step=50)
    spx_df = fetchDataIndex("SPX", trading_day, trading_day).reset_index()
    S = spx_df.loc[0, "Open"]
    atm_strike = round(S / 50) * 50
    strikes = np.arange(atm_strike - 200, atm_strike + 201, 50)
    
    # Calculate IV surface
    surface_df = calculate_iv_surface(trading_day, expiry_days, strikes)
    
    if surface_df is None or surface_df.empty:
        print("No valid surface data calculated.")
    else:
        # Export to Excel
        surface_df.to_excel("spxw_iv_surface.xlsx", index=False)
        print("Surface data exported to spxw_iv_surface.xlsx")
        
        # Prepare data for 3D plot
        pivot_df = surface_df.pivot(index="Days_to_Expiry", columns="Strike", values="Call_IV")
        strikes = pivot_df.columns
        expiries = pivot_df.index
        iv_matrix = pivot_df.values
        
        # Visualize IV surface
        fig = go.Figure(data=[go.Surface(z=iv_matrix, x=strikes, y=expiries)])
        fig.update_layout(
            title=f"SPXW IV Surface ({trading_day})",
            scene=dict(
                xaxis_title="Strike Price ($)",
                yaxis_title="Days to Expiry",
                zaxis_title="Implied Volatility (%)"
            ),
            width=800,
            height=600
        )
        fig.write_to_png("iv_surface.png")
        fig.show()