import numpy as np
import matplotlib.pyplot as plt

# Black-Scholes for option pricing and Greeks
def black_scholes_greeks(S, K, T, r, sigma, option_type="call"):
    """Calculate Black-Scholes price, delta, and gamma."""
    from scipy.stats import norm
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    return price, delta, gamma

# Gamma scalping simulation
def gamma_scalping(S, K, T, r, sigma, price_path, hedge_interval=0.01):
    """Simulate gamma scalping on a long straddle."""
    call_price, call_delta, call_gamma = black_scholes_greeks(S, K, T, r, sigma, "call")
    put_price, put_delta, put_gamma = black_scholes_greeks(S, K, T, r, sigma, "put")
    
    # Initial straddle: Buy call + put
    initial_cost = call_price + put_price
    total_delta = call_delta + put_delta  # Near zero for ATM straddle
    total_gamma = call_gamma + put_gamma
    
    # Simulate price path (input or generated)
    times = np.arange(0, T, hedge_interval)
    profits = []
    stock_position = 0
    cumulative_profit = 0
    
    for t, S_t in zip(times, price_path):
        # Update Greeks
        T_remaining = T - t
        if T_remaining <= 0:
            break
        _, call_delta, call_gamma = black_scholes_greeks(S_t, K, T_remaining, r, sigma, "call")
        _, put_delta, put_gamma = black_scholes_greeks(S_t, K, T_remaining, r, sigma, "put")
        new_delta = call_delta + put_delta
        
        # Hedge: Adjust stock position to neutralize delta
        delta_change = new_delta - total_delta
        stock_trade = -delta_change  # Buy/sell stocks to offset
        stock_position += stock_trade
        trade_cost = stock_trade * S_t
        cumulative_profit -= trade_cost
        
        # Update total delta
        total_delta = new_delta
    
    # At expiration: Close straddle and stock position
    final_payoff = max(price_path[-1] - K, 0) + max(K - price_path[-1], 0) - initial_cost
    stock_close_profit = -stock_position * price_path[-1]
    cumulative_profit += final_payoff + stock_close_profit
    
    return times, [cumulative_profit] * len(times), call_price, put_price, call_delta, put_delta, total_gamma

# Filters for trade selection
def apply_gamma_scalping_filters(S, K, T, r, sigma):
    """Apply filters: IV > 30%, T in [7, 30] days, delta in [0.4, 0.6]."""
    _, call_delta, _ = black_scholes_greeks(S, K, T, r, sigma, "call")
    days_to_expiry = T * 365
    
    if sigma < 0.30:  # IV < 30%
        return False, "IV too low (<30%)"
    if not (7 <= days_to_expiry <= 30):
        return False, f"Time to expiry ({days_to_expiry:.0f} days) outside [7, 30]"
    if not (0.4 <= call_delta <= 0.6):
        return False, f"Call delta ({call_delta:.3f}) outside [0.4, 0.6]"
    
    return True, "Filters passed"

# Main function
def run_gamma_scalping(S=5300, K=5300, T=30/365, r=0.02, sigma=0.35, hedge_interval=0.01):
    """Run gamma scalping strategy with filters."""
    # Apply filters
    is_valid, message = apply_gamma_scalping_filters(S, K, T, r, sigma)
    if not is_valid:
        print(f"Gamma scalping rejected: {message}")
        return
    
    # Generate synthetic price path (replace with real data later)
    np.random.seed(42)
    times = np.arange(0, T, hedge_interval)
    price_path = S * np.exp((r - 0.5 * sigma**2) * times + sigma * np.sqrt(hedge_interval) * np.cumsum(np.random.randn(len(times))))
    
    # Run simulation
    times, profits, call_price, put_price, call_delta, put_delta, total_gamma = gamma_scalping(
        S, K, T, r, sigma, price_path, hedge_interval
    )
    
    # Print details
    print(f"Gamma Scalping (Long Straddle): S=${S}, K=${K}, T={T*365:.0f} days, IV={sigma*100:.1f}%")
    print(f"Call Price: ${call_price:.2f}, Delta: {call_delta:.3f}")
    print(f"Put Price: ${put_price:.2f}, Delta: {put_delta:.3f}")
    print(f"Total Premium: ${call_price + put_price:.2f}, Gamma: {total_gamma:.4f}")
    print(f"Final Profit: ${profits[-1]:.2f}")
    
    # Plot cumulative profit
    plt.figure(figsize=(10, 6))
    plt.plot(times * 365, profits, label="Cumulative Profit")
    plt.axhline(0, color='k', linestyle='--', alpha=0.3)
    plt.title(f"Gamma Scalping Profit (K=${K}, IV={sigma*100:.1f}%)")
    plt.xlabel("Days")
    plt.ylabel("Profit/Loss ($)")
    plt.legend()
    plt.grid()
    plt.savefig("gamma_scalping_profit.png")
    plt.show()

if __name__ == "__main__":
    # Example: Gamma scalping
    run_gamma_scalping()