import numpy as np
import matplotlib.pyplot as plt

# Black-Scholes for option pricing
def black_scholes(S, K, T, r, sigma, option_type="call"):
    """Calculate Black-Scholes option price and delta."""
    from scipy.stats import norm
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
    
    return price, delta

# Strangle payoff calculation
def strangle_payoff(S, K_call, K_put, T, r, sigma, strategy="long"):
    """Calculate strangle P/L for long or short."""
    call_price, call_delta = black_scholes(S, K_call, T, r, sigma, "call")
    put_price, put_delta = black_scholes(S, K_put, T, r, sigma, "put")
    
    # Long strangle: Buy OTM call + put
    if strategy == "long":
        premium = call_price + put_price
        # Payoff at expiration
        S_range = np.linspace(S * 0.8, S * 1.2, 100)  # ±20% price range
        payoff = np.maximum(S_range - K_call, 0) + np.maximum(K_put - S_range, 0) - premium
    # Short strangle: Sell OTM call + put
    else:
        premium = call_price + put_price
        S_range = np.linspace(S * 0.8, S * 1.2, 100)
        payoff = premium - (np.maximum(S_range - K_call, 0) + np.maximum(K_put - S_range, 0))
    
    return S_range, payoff, call_price, put_price, call_delta, put_delta

# Filters for trade selection
def apply_strangle_filters(S, K_call, K_put, T, r, sigma):
    """Apply filters: IV > 25%, T in [7, 60] days, delta in [0.2, 0.4]."""
    _, call_delta = black_scholes(S, K_call, T, r, sigma, "call")
    _, put_delta = black_scholes(S, K_put, T, r, sigma, "put")
    days_to_expiry = T * 365
    
    if sigma < 0.25:  # IV < 25%
        return False, "IV too low (<25%)"
    if not (7 <= days_to_expiry <= 60):
        return False, f"Time to expiry ({days_to_expiry:.0f} days) outside [7, 60]"
    if not (0.2 <= call_delta <= 0.4) or not (-0.4 <= put_delta <= -0.2):
        return False, f"Deltas (Call: {call_delta:.3f}, Put: {put_delta:.3f}) outside [0.2, 0.4]"
    
    return True, "Filters passed"

# Main function
def run_strangle(S=5300, K_call=5400, K_put=5200, T=30/365, r=0.02, sigma=0.35, strategy="long"):
    """Run strangle strategy with filters."""
    # Apply filters
    is_valid, message = apply_strangle_filters(S, K_call, K_put, T, r, sigma)
    if not is_valid:
        print(f"Strangle rejected: {message}")
        return
    
    # Calculate payoff
    S_range, payoff, call_price, put_price, call_delta, put_delta = strangle_payoff(S, K_call, K_put, T, r, sigma, strategy)
    
    # Print details
    print(f"{strategy.capitalize()} Strangle: S=${S}, K_call=${K_call}, K_put=${K_put}, T={T*365:.0f} days, IV={sigma*100:.1f}%")
    print(f"Call Price: ${call_price:.2f}, Delta: {call_delta:.3f}")
    print(f"Put Price: ${put_price:.2f}, Delta: {put_delta:.3f}")
    print(f"Total Premium: ${call_price + put_price:.2f}")
    
    # Plot payoff
    plt.figure(figsize=(10, 6))
    plt.plot(S_range, payoff, label=f"{strategy.capitalize()} Strangle Payoff")
    plt.axhline(0, color='k', linestyle='--', alpha=0.3)
    plt.axvline(S, color='k', linestyle='--', label="Current Price")
    plt.title(f"{strategy.capitalize()} Strangle Payoff (K_call=${K_call}, K_put=${K_put}, IV={sigma*100:.1f}%)")
    plt.xlabel("Stock Price ($)")
    plt.ylabel("Profit/Loss ($)")
    plt.legend()
    plt.grid()
    plt.savefig(f"{strategy}_strangle_payoff.png")
    plt.show()

if __name__ == "__main__":
    # Example: Long strangle
    run_strangle(strategy="long")
    # Example: Short strangle
    run_strangle(strategy="short")