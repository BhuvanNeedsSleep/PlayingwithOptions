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

# Diagonal spread payoff calculation
def diagonal_spread_payoff(S, K_near, K_far, T_near, T_far, r, sigma_near, sigma_far, option_type="call", strategy="long"):
    """Calculate diagonal spread P/L at near-month expiration."""
    # Near-month option (sell for long, buy for short)
    near_price, near_delta = black_scholes(S, K_near, T_near, r, sigma_near, option_type)
    # Far-month option (buy for long, sell for short)
    far_price, far_delta = black_scholes(S, K_far, T_far, r, sigma_far, option_type)
    
    # Long: Buy far-month lower strike, sell near-month higher strike (for calls)
    if strategy == "long":
        cost = far_price - near_price
        S_range = np.linspace(S * 0.9, S * 1.1, 100)  # ±10% price range
        payoff = np.zeros_like(S_range)
        for i, s in enumerate(S_range):
            far_remaining, _ = black_scholes(s, K_far, T_far - T_near, r, sigma_far, option_type)
            payoff[i] = far_remaining - cost  # Near-month expires
    # Short: Sell far-month lower strike, buy near-month higher strike
    else:
        cost = near_price - far_price
        S_range = np.linspace(S * 0.9, S * 1.1, 100)
        payoff = np.zeros_like(S_range)
        for i, s in enumerate(S_range):
            far_remaining, _ = black_scholes(s, K_far, T_far - T_near, r, sigma_far, option_type)
            payoff[i] = cost - far_remaining
    
    return S_range, payoff, near_price, far_price, near_delta, far_delta

# Filters for trade selection
def apply_diagonal_filters(S, K_near, K_far, T_near, T_far, r, sigma_near, sigma_far, option_type="call"):
    """Apply filters: front-month IV > 30%, expiration gap 14-60 days, near-month delta 0.4-0.6."""
    _, near_delta = black_scholes(S, K_near, T_near, r, sigma_near, option_type)
    days_near = T_near * 365
    days_far = T_far * 365
    expiration_gap = days_far - days_near
    
    if sigma_near < 0.3:  # Front-month IV < 30%
        return False, "Front-month IV too low (<30%)"
    if not (14 <= expiration_gap <= 60):
        return False, f"Expiration gap ({expiration_gap:.0f} days) outside [14, 60]"
    if not (0.4 <= near_delta <= 0.6):
        return False, f"Near-month delta ({near_delta:.3f}) outside [0.4, 0.6]"
    
    return True, "Filters passed"

# Main function
def run_diagonal_spread(S=5300, K_near=5400, K_far=5300, T_near=7/365, T_far=30/365, r=0.02, sigma_near=0.35, sigma_far=0.25, option_type="call", strategy="long"):
    """Run diagonal spread strategy with filters."""
    # Apply filters
    is_valid, message = apply_diagonal_filters(S, K_near, K_far, T_near, T_far, r, sigma_near, sigma_far, option_type)
    if not is_valid:
        print(f"Diagonal spread rejected: {message}")
        return
    
    # Calculate payoff
    S_range, payoff, near_price, far_price, near_delta, far_delta = diagonal_spread_payoff(
        S, K_near, K_far, T_near, T_far, r, sigma_near, sigma_far, option_type, strategy
    )
    
    # Print details
    print(f"{strategy.capitalize()} {option_type.capitalize()} Diagonal Spread: S=${S}, K_near=${K_near}, K_far=${K_far}, T_near={T_near*365:.0f} days, T_far={T_far*365:.0f} days")
    print(f"Near-month IV: {sigma_near*100:.1f}%, Far-month IV: {sigma_far*100:.1f}%")
    print(f"Near-month Price: ${near_price:.2f}, Delta: {near_delta:.3f}")
    print(f"Far-month Price: ${far_price:.2f}, Delta: {far_delta:.3f}")
    print(f"Net Cost: ${abs(far_price - near_price):.2f} {'Debit' if strategy == 'long' else 'Credit'}")
    
    # Plot payoff
    plt.figure(figsize=(10, 6))
    plt.plot(S_range, payoff, label=f"{strategy.capitalize()} Diagonal Spread Payoff")
    plt.axhline(0, color='k', linestyle='--', alpha=0.3)
    plt.axvline(S, color='k', linestyle='--', label="Current Price")
    plt.title(f"{strategy.capitalize()} {option_type.capitalize()} Diagonal Spread Payoff (K_near=${K_near}, IV_near={sigma_near*100:.1f}%)")
    plt.xlabel("Stock Price ($)")
    plt.ylabel("Profit/Loss ($)")
    plt.legend()
    plt.grid()
    plt.savefig(f"{strategy}_diagonal_spread_{option_type}.png")
    plt.show()

if __name__ == "__main__":
    # Example: Long call diagonal spread
    run_diagonal_spread(strategy="long", option_type="call")
    # Example: Short call diagonal spread
    run_diagonal_spread(strategy="short", option_type="call")