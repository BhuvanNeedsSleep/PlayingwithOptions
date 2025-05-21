import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
from fetchData import fetchDataIndex, fetchDataOptions  # Your SPX/SPXW data fetcher

# Black-Scholes formula for call and put prices
def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    # Greeks
    delta = norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) * 0.01  # Per 1% IV change
    theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365  # Daily
    
    return price, delta, gamma, vega, theta

# Fetch SPX data for May 15, 2024
trading_day = "2024-05-15"
expiry_day = "2024-05-31"
spx_df = fetchDataIndex("SPX", trading_day, trading_day).reset_index()
S = spx_df.loc[0, "Open"]  # SPX open price
K = round(S / 50) * 50  # ATM strike
T = (pd.to_datetime(expiry_day) - pd.to_datetime(trading_day)).days / 365  # Time to expiry
r = 0.02  # Risk-free rate
sigma = 0.3  # Implied volatility (30%)

# Calculate prices and Greeks
call_price, call_delta, call_gamma, call_vega, call_theta = black_scholes(S, K, T, r, sigma, "call")
put_price, put_delta, put_gamma, put_vega, put_theta = black_scholes(S, K, T, r, sigma, "put")

# Print results
print(f"SPX Open: ${S:.2f}, Strike: ${K}, Expiry: {expiry_day}")
print(f"Call Price: ${call_price:.2f}, Delta: {call_delta:.3f}, Gamma: {call_gamma:.3f}, Vega: {call_vega:.3f}, Theta: {call_theta:.3f}")
print(f"Put Price: ${put_price:.2f}, Delta: {put_delta:.3f}, Gamma: {put_gamma:.3f}, Vega: {put_vega:.3f}, Theta: {put_theta:.3f}")

# Visualize Greeks sensitivity
S_range = np.linspace(S * 0.9, S * 1.1, 100)  # Stock price range (±10%)
call_deltas, call_gammas = [], []
for s in S_range:
    _, delta, gamma, _, _ = black_scholes(s, K, T, r, sigma, "call")
    call_deltas.append(delta)
    call_gammas.append(gamma)

plt.figure(figsize=(10, 6))
plt.plot(S_range, call_deltas, label="Call Delta")
plt.plot(S_range, call_gammas, label="Call Gamma")
plt.axvline(S, color='k', linestyle='--', label="Current SPX")
plt.title("Call Delta and Gamma vs. SPX Price")
plt.xlabel("SPX Price ($)")
plt.ylabel("Value")
plt.legend()
plt.grid()
plt.savefig("greeks_sensitivity.png")
plt.show()