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

# Vertical spread payoff calculation
def vertical_spread_payoff(S, K1, K2, T, r, sigma, option_type="call", strategy="long"):
    """Calculate vertical spread P/L for bull call or bear put spread."""
    # For calls: K1 < K2; for puts: K1 > K2
    price1, delta1 = black_scholes(S, K1, T, r, sigma, option_type)
    price2, delta2 = black_scholes(S, K2, T, r, sigma, option_type)
    
    # Long bull call: Buy K1 call, sell K2 call; Long bear put: Buy K1 put, sell K2 put
    if strategy == "long":
        cost = price1 - price2  # Debit
        S_range = np.linspace(S * 0.9, S * 1.1, 100)  # ±10% price range
        if option_type == "call":
            payoff = np.maximum(S_range - K1, 0) - np.maximum(S_range - K2, 0) - cost
        else:
            payoff = np.maximum(K1 - S_range, 0) - np.maximum(K2 - S_range, 0) - cost
    # Short bull call: Sell K1 call, buy K2 call; Short bear put: Sell K1 put, buy K2 put
    else:
        cost = price2 - price1  # Credit
        S_range = np.linspace(S * 0.9, S * 1.1, 100)
        if option_type == "call":
            payoff = cost - (np.maximum(S_range - K1, 0) - np.maximum(S_range - K2, 0))
        else:
            payoff = cost - (np.maximum(K1 - S_range, 0) - np.maximum(K2 - S_range, 0))
    
    return S_range, payoff, price1, price2, delta1, delta2

# Filters for trade selection
def apply_vertical_filters(S, K1, K2, T, r, sigma, option_type="call"):
    """Apply filters: IV > 25%, T in [7, 60] days, delta difference 0.1-0.3."""
    _, delta1 = black_scholes(S, K1, T, r, sigma, option_type)
    _, delta2 = black_scholes(S, K2, T, r, sigma, option_type)
    days_to_expiry = T * 365
    delta_diff = abs(delta1 - delta2)
    
    if sigma < 0.25:  # IV < 25%
        return False, "IV too low (<25%)"
    if not (7 <= days_to_expiry <= 60):
        return False, f"Time to expiry ({days_to_expiry:.0f} days) outside [7, 60]"
    if not (0.1 <= delta_diff <= 0.3):
        return False, f"Delta difference ({delta_diff:.3f}) outside [0.1, 0.3]"
    
    return True, "Filters passed"

# Main function
def run_vertical_spread(S=5300, K1=5300, K2=5400, T=30/365, r=0.02, sigma=0.30, option_type="call", strategy="long"):
    """Run vertical spread strategy with filters."""
    # Adjust K1, K2 for puts (bear put: K1 > K2)
    if option_type == "put" and K1 < K2:
        K1, K2 = K2, K1
    
    # Apply filters
    is_valid, message = apply_vertical_filters(S, K1, K2, T, r, sigma, option_type)
    if not is_valid:
        print(f"Vertical spread rejected: {message}")
        return
    
    # Calculate payoff
    S_range, payoff, price1, price2, delta1, delta2 = vertical_spread_payoff(
        S, K1, K2, T, r, sigma, option_type, strategy
    )
    
    # Print details
    spread_type = "Bull Call" if option_type == "call" else "Bear Put"
    print(f"{strategy.capitalize()} {spread_type} Spread: S=${S}, K1=${K1}, K2=${K2}, T={T*365:.0f} days, IV={sigma*100:.1f}%")
    print(f"K1 {option_type.capitalize()} Price: ${price1:.2f}, Delta: {delta1:.3f}")
    print(f"K2 {option_type.capitalize()} Price: ${price2:.2f}, Delta: {delta2:.3f}")
    print(f"Net Cost: ${abs(price1 - price2):.2f} {'Debit' if strategy == 'long' else 'Credit'}")
    
    # Plot payoff
    plt.figure(figsize=(10, 6))
    plt.plot(S_range, payoff, label=f"{strategy.capitalize()} {spread_type} Payoff")
    plt.axhline(0, color='k', linestyle='--', alpha=0.3)
    plt.axvline(S, color='k', linestyle='--', label="Current Price")
    plt.title(f"{strategy.capitalize()} {spread_type} Payoff (K1=${K1}, K2=${K2}, IV={sigma*100:.1f}%)")
    plt.xlabel("Stock Price ($)")
    plt.ylabel("Profit/Loss ($)")
    plt.legend()
    plt.grid()
    plt.savefig(f"{strategy}_vertical_spread_{option_type}.png")
    plt.show()

if __name__ == "__main__":
    # Example: Long bull call spread
    run_vertical_spread(strategy="long", option_type="call")
    # Example: Short bull call spread
    run_vertical_spread(strategy="short", option_type="call")
    # Example: Long bear put spread
    run_vertical_spread(strategy="long", option_type="put", K1=5400, K2=5300)