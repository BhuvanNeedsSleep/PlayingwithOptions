import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
from arch import arch_model
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

# Fetch and calculate daily ATM IV
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
                "Call_IV": call_iv * 100,  # In percentage
                "Time_to_Expiry": T * 365
            })
    
    return pd.DataFrame(iv_data)

# Fit GARCH(1,1) model and forecast IV
def fit_garch_model(iv_df, forecast_horizon=5):
    """Fit GARCH(1,1) to IV and forecast future volatility."""
    # Prepare IV returns (log differences for stationarity)
    iv_series = iv_df["Call_IV"].values
    iv_returns = 100 * np.diff(np.log(iv_series))  # Percentage log returns
    
    # Filter: Ensure enough data points
    if len(iv_returns) < 5:
        print("Insufficient data for GARCH modeling.")
        return None
    
    # Fit GARCH(1,1)
    model = arch_model(iv_returns, vol="Garch", p=1, q=1, mean="Zero")
    try:
        garch_fit = model.fit(disp="off")
    except Exception as e:
        print(f"GARCH fitting error: {e}")
        return None
    
    # Forecast volatility
    forecast = garch_fit.forecast(horizon=forecast_horizon)
    forecast_vol = np.sqrt(forecast.variance.values[-1, :])  # Annualized volatility
    
    # Convert back to IV levels (approximate)
    last_iv = iv_series[-1]
    forecast_iv = last_iv * np.exp(np.cumsum(forecast_vol / 100))
    
    # Confidence intervals (approximate, using volatility of volatility)
    vol_std = np.std(iv_returns)
    ci_upper = forecast_iv + 1.96 * vol_std * np.sqrt(np.arange(1, forecast_horizon + 1))
    ci_lower = forecast_iv - 1.96 * vol_std * np.sqrt(np.arange(1, forecast_horizon + 1))
    
    return forecast_iv, ci_lower, ci_upper, garch_fit

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
        # Fit GARCH model and forecast
        forecast_horizon = 5
        garch_result = fit_garch_model(iv_df, forecast_horizon)
        
        if garch_result is None:
            print("GARCH modeling failed.")
        else:
            forecast_iv, ci_lower, ci_upper, garch_fit = garch_result
            
            # Prepare forecast DataFrame
            forecast_dates = [iv_df["Date"].iloc[-1] + datetime.timedelta(days=i) for i in range(1, forecast_horizon + 1)]
            forecast_df = pd.DataFrame({
                "Date": forecast_dates,
                "Forecast_IV": forecast_iv,
                "CI_Lower": ci_lower,
                "CI_Upper": ci_upper
            })
            
            # Combine historical and forecast data
            combined_df = pd.concat([iv_df, forecast_df], ignore_index=True)
            
            # Export to Excel
            combined_df.to_excel("spxw_garch_iv_forecast.xlsx", index=False)
            print("GARCH forecast exported to spxw_garch_iv_forecast.xlsx")
            
            # Visualize historical and forecasted IV
            plt.figure(figsize=(12, 6))
            plt.plot(iv_df["Date"], iv_df["Call_IV"], marker="o", label="Historical Call IV")
            plt.plot(forecast_df["Date"], forecast_df["Forecast_IV"], marker="s", label="Forecasted IV")
            plt.fill_between(forecast_df["Date"], forecast_df["CI_Lower"], forecast_df["CI_Upper"], alpha=0.2, label="95% CI")
            plt.title(f"SPXW ATM Call IV with GARCH(1,1) Forecast ({trading_days[0]} to {forecast_dates[-1]})")
            plt.xlabel("Date")
            plt.ylabel("Implied Volatility (%)")
            plt.legend()
            plt.grid()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("garch_iv_forecast.png")
            plt.show()
            
            # Print GARCH parameters
            print("\nGARCH(1,1) Parameters:")
            print(garch_fit.summary())