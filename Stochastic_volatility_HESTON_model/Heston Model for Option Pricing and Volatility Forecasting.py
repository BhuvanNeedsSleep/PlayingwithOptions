import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq, minimize
from fetchData import fetchDataIndex, fetchDataOptions
import matplotlib.pyplot as plt
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

# Fetch daily ATM IV
def fetch_daily_atm_iv(trading_days, expiry_day, r=0.02):
    """Fetch SPX/SPXW data and calculate daily ATM call IV."""
    iv_data = []
    
    for day in trading_days:
        print(f"Processing {day}")
        # Fetch SPX data
        try:
            spx_df = fetchDataIndex("SPX", day, day).reset_index()
            S = spx_df.loc[0, "Open"]
        except Exception as e:
            print(f"SPX fetch error on {day}: {e}")
            continue
        
        # ATM strike
        strike = round(S / 50) * 50
        T = (pd.to_datetime(expiry_day) - pd.to_datetime(day)).days / 365
        
        # Filter: Ensure T is 7-60 days
        if not (7 <= T * 365 <= 60):
            print(f"Time to expiry ({T*365:.0f} days) outside [7, 60] for {day}")
            continue
        
        # Fetch call data
        try:
            ce_df = fetchDataOptions("SPXW", day, day, strike, expiry_day, "CE").reset_index()
        except Exception as e:
            print(f"Option fetch error on {day}, strike {strike}: {e}")
            continue
        
        # Use first minute's open price
        call_price = ce_df.loc[0, "Open"] if not ce_df.empty else np.nan
        
        # Filter: Ensure price is positive
        if np.isnan(call_price) or call_price <= 0:
            print(f"Invalid call price on {day}, strike {strike}: ${call_price}")
            continue
        
        # Calculate IV
        call_iv = implied_volatility(S, strike, T, r, call_price, "call")
        
        if not np.isnan(call_iv):
            iv_data.append({
                "Date": day,
                "SPX_Open": S,
                "Strike": strike,
                "Call_IV": call_iv,
                "Time_to_Expiry": T
            })
    
    return pd.DataFrame(iv_data)

# Heston model Monte Carlo simulation
def heston_simulation(S0, v0, kappa, theta, sigma_v, rho, r, T, n_steps, n_paths):
    """Simulate Heston model paths for price and variance."""
    dt = T / n_steps
    price_paths = np.zeros((n_paths, n_steps + 1))
    vol_paths = np.zeros((n_paths, n_steps + 1))
    price_paths[:, 0] = S0
    vol_paths[:, 0] = v0
    
    # Correlated Brownian motions
    z1 = np.random.normal(0, 1, (n_paths, n_steps))
    z2 = rho * z1 + np.sqrt(1 - rho**2) * np.random.normal(0, 1, (n_paths, n_steps))
    
    for t in range(n_steps):
        # Variance process (CIR)
        vol_paths[:, t+1] = np.maximum(
            vol_paths[:, t] + kappa * (theta - vol_paths[:, t]) * dt + 
            sigma_v * np.sqrt(vol_paths[:, t]) * np.sqrt(dt) * z2[:, t], 
            0
        )
        # Price process
        price_paths[:, t+1] = price_paths[:, t] * np.exp(
            (r - 0.5 * vol_paths[:, t]) * dt + 
            np.sqrt(vol_paths[:, t]) * np.sqrt(dt) * z1[:, t]
        )
    
    return price_paths, vol_paths

# Heston option pricing
def heston_option_price(S0, K, v0, kappa, theta, sigma_v, rho, r, T, n_steps, n_paths, option_type="call"):
    """Price option using Heston model Monte Carlo."""
    price_paths, _ = heston_simulation(S0, v0, kappa, theta, sigma_v, rho, r, T, n_steps, n_paths)
    if option_type == "call":
        payoffs = np.maximum(price_paths[:, -1] - K, 0)
    else:
        payoffs = np.maximum(K - price_paths[:, -1], 0)
    return np.exp(-r * T) * np.mean(payoffs)

# Calibrate Heston model
def calibrate_heston(iv_df, S0, K, T, r, n_steps=100, n_paths=1000):
    """Calibrate Heston parameters to ATM call IVs."""
    market_prices = []
    for _, row in iv_df.iterrows():
        market_prices.append(
            black_scholes_price(row["SPX_Open"], row["Strike"], row["Time_to_Expiry"], r, row["Call_IV"])
        )
    
    def objective(params):
        v0, kappa, theta, sigma_v, rho = params
        model_prices = [
            heston_option_price(row["SPX_Open"], row["Strike"], v0, kappa, theta, sigma_v, rho, r, 
                               row["Time_to_Expiry"], n_steps, n_paths) 
            for _, row in iv_df.iterrows()
        ]
        return np.sum((np.array(model_prices) - np.array(market_prices))**2)
    
    # Initial guess: [v0, kappa, theta, sigma_v, rho]
    initial_guess = [0.04, 2.0, 0.04, 0.3, -0.7]
    bounds = [(0.01, 0.1), (0.1, 5.0), (0.01, 0.1), (0.01, 1.0), (-1.0, 1.0)]
    
    try:
        result = minimize(objective, initial_guess, bounds=bounds, method="SLSQP")
        return result.x
    except Exception as e:
        print(f"Calibration error: {e}")
        return None

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
    
    # Fetch daily ATM IV
    iv_df = fetch_daily_atm_iv(trading_days, expiry_day)
    
    if iv_df.empty:
        print("No valid IV data calculated.")
    else:
        # Latest data for simulation
        S0 = iv_df["SPX_Open"].iloc[-1]
        K = iv_df["Strike"].iloc[-1]
        T = iv_df["Time_to_Expiry"].iloc[-1]
        
        # Calibrate Heston model
        heston_params = calibrate_heston(iv_df, S0, K, T, r=0.02)
        
        if heston_params is None:
            print("Heston calibration failed.")
        else:
            v0, kappa, theta, sigma_v, rho = heston_params
            print(f"Heston Parameters: v0={v0:.4f}, kappa={kappa:.4f}, theta={theta:.4f}, sigma_v={sigma_v:.4f}, rho={rho:.4f}")
            
            # Simulate paths
            n_steps = 100
            n_paths = 1000
            price_paths, vol_paths = heston_simulation(S0, v0, kappa, theta, sigma_v, rho, r=0.02, T=T, n_steps=n_steps, n_paths=n_paths)
            
            # Price option
            call_price = heston_option_price(S0, K, v0, kappa, theta, sigma_v, rho, r=0.02, T=T, n_steps=n_steps, n_paths=n_paths, option_type="call")
            print(f"Heston Call Price (K=${K}): ${call_price:.2f}")
            
            # Prepare output DataFrame
            output_df = pd.DataFrame({
                "Time_Step": np.arange(n_steps + 1) * T / n_steps * 365,
                "Mean_Price": np.mean(price_paths, axis=0),
                "Mean_Volatility": np.sqrt(np.mean(vol_paths, axis=0)) * 100
            })
            
            # Export to Excel
            output_df.to_excel("spxw_heston_simulation.xlsx", index=False)
            print("Heston simulation exported to spxw_heston_simulation.xlsx")
            
            # Visualize paths
            plt.figure(figsize=(12, 8))
            
            # Price paths
            plt.subplot(2, 1, 1)
            for i in range(min(10, n_paths)):
                plt.plot(output_df["Time_Step"], price_paths[i], alpha=0.3)
            plt.plot(output_df["Time_Step"], output_df["Mean_Price"], "k", label="Mean Price")
            plt.title(f"Heston Price Paths (S0=${S0}, T={T*365:.0f} days)")
            plt.xlabel("Days")
            plt.ylabel("SPX Price ($)")
            plt.legend()
            plt.grid()
            
            # Volatility paths
            plt.subplot(2, 1, 2)
            for i in range(min(10, n_paths)):
                plt.plot(output_df["Time_Step"], np.sqrt(vol_paths[i]) * 100, alpha=0.3)
            plt.plot(output_df["Time_Step"], output_df["Mean_Volatility"], "k", label="Mean Volatility")
            plt.title("Heston Volatility Paths")
            plt.xlabel("Days")
            plt.ylabel("Volatility (%)")
            plt.legend()
            plt.grid()
            
            plt.tight_layout()
            plt.savefig("heston_simulation.png")
            plt.show()