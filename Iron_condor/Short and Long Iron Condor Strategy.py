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

# Iron condor payoff calculation
def iron_condor_payoff(S, K_put_sell, K_put_buy, K_call_sell, K_call_buy, T, r, sigma, strategy="short"):
    """Calculate iron condor P/L."""
    # Prices and deltas
    put_sell_price, put_sell_delta = black_scholes(S, K_put_sell, T, r, sigma, "put")
    put_buy_price, put_buy_delta = black_scholes(S, K_put_buy, T, r, sigma, "put")
    call_sell_price, call_sell_delta = black_scholes(S, K_call_sell, T, r, sigma, "call")
    call_buy_price, call_buy_delta = black_scholes(S, K_call_buy, T, r, sigma, "call")
    
    # Short iron condor: Sell put spread (sell K_put_sell, buy K_put_buy), sell call spread
    if strategy == "short":
        credit = (put_sell_price - put_buy_price) + (call_sell_price - call_buy_price)
        S_range = np.linspace(S * 0.85, S * 1.15, 100)  # ±15% price range
        payoff = credit - (
            np.maximum(K_put_sell - S_range, 0) - np.maximum(K_put_buy - S_range, 0) +
            np.maximum(S_range - K_call_sell, 0) - np.maximum(S_range - K_call_buy, 0)
        )
    # Long iron condor: Buy put spread, buy call spread
    else:
        debit = (put_buy_price - put_sell_price) + (call_buy_price - call_sell_price)
        S_range = np.linspace(S * 0.85, S * 1.15, 100)
        payoff = (
            np.maximum(K_put_buy - S_range, 0) - np.maximum(K_put_sell - S_range, 0) +
            np.maximum(S_range - K_call_buy, 0) - np.maximum(S_range - K_call_sell, 0)
        ) - debit
    
    return S_range, payoff, put_sell_price, put_buy_price, call_sell_price, call_buy_price, put_sell_delta, call_sell_delta

# Filters for trade selection
def apply_iron_condor_filters(S, K_put_sell, K_put_buy, K_call_sell, K_call_buy, T, r, sigma):
    """Apply filters: IV > 25%, T in [7, 60] days, wing delta in [0.1, 0.3]."""
    _, put_sell_delta = black_scholes(S, K_put_sell, T, r, sigma, "put")
    _, call_sell_delta = black_scholes(S, K_call_sell, T, r, sigma, "call")
    days_to_expiry = T * 365
    
    if sigma < 0.25:  # IV < 25%
        return False, "IV too low (<25%)"
    if not (7 <= days_to_expiry <= 60):
        return False, f"Time to expiry ({days_to_expiry:.0f} days) outside [7, 60]"
    if not (-0.3 <= put_sell_delta <= -0.1) or not (0.1 <= call_sell_delta <= 0.3):
        return False, f"Deltas (Put: {put_sell_delta:.3f}, Call: {call_sell_delta:.3f}) outside [0.1, 0.3]"
    
    return True, "Filters passed"

# Main function
def run_iron_condor(S=5300, K_put_buy=5100, K_put_sell=5200, K_call_sell=5400, K_call_buy=5500, T=30/365, r=0.02, sigma=0.30, strategy="short"):
    """Run iron condor strategy with filters."""
    # Apply filters
    is_valid, message = apply_iron_condor_filters(S, K_put_sell, K_put_buy, K_call_sell, K_call_buy, T, r, sigma)
    if not is_valid:
        print(f"Iron condor rejected: {message}")
        return
    
    # Calculate payoff
    S_range, payoff, put_sell_price, put_buy_price, call_sell_price, call_buy_price, put_sell_delta, call_sell_delta = iron_condor_payoff(
        S, K_put_sell, K_put_buy, K_call_sell, K_call_buy, T, r, sigma, strategy
    )
    
    # Print details
    print(f"{strategy.capitalize()} Iron Condor: S=${S}, T={T*365:.0f} days, IV={sigma*100:.1f}%")
    print(f"Sell Put K=${K_put_sell}: ${put_sell_price:.2f}, Delta: {put_sell_delta:.3f}")
    print(f"Buy Put K=${K_put_buy}: ${put_buy_price:.2f}")
    print(f"Sell Call K=${K_call_sell}: ${call_sell_price:.2f}, Delta: {call_sell_delta:.3f}")
    print(f"Buy Call K=${K_call_buy}: ${call_buy_price:.2f}")
    net = abs((put_sell_price - put_buy_price) + (call_sell_price - call_buy_price))
    print(f"Net {'Credit' if strategy == 'short' else 'Debit'}: ${net:.2f}")
    
    # Plot payoff
    plt.figure(figsize=(10, 6))
    plt.plot(S_range, payoff, label=f"{strategy.capitalize()} Iron Condor Payoff")
    plt.axhline(0, color='k', linestyle='--', alpha=0.3)
    plt.axvline(S, color='k', linestyle='--', label="Current Price")
    plt.title(f"{strategy.capitalize()} Iron Condor Payoff (IV={sigma*100:.1f}%)")
    plt.xlabel("Stock Price ($)")
    plt.ylabel("Profit/Loss ($)")
    plt.legend()
    plt.grid()
    plt.savefig(f"{strategy}_iron_condor.png")
    plt.show()

if __name__ == "__main__":
    # Example: Short iron condor
    run_iron_condor(strategy="short")
    # Example: Long iron condor
    run_iron_condor(strategy="long")