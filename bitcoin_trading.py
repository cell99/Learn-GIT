import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# The prompt asks for 60 days of data explicitly.
np.random.seed(111) # Change seed to find a path that crosses

# Simulation parameters
days = 60
initial_price = 50000.0
mu = 0.001 # Drift (daily)
sigma = 0.05 # Increased Volatility (daily) to try and force a cross within 60 days

# Generate price data using Geometric Brownian Motion
dt = 1
prices = [initial_price]
for i in range(1, days):
    shock = np.random.normal(0, 1)
    new_price = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * shock)
    prices.append(new_price)

dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
df = pd.DataFrame({'Date': dates, 'Price': prices})

# Calculate 7-day and 30-day Moving Averages
df['7-day MA'] = df['Price'].rolling(window=7).mean()
df['30-day MA'] = df['Price'].rolling(window=30).mean()

initial_balance = 10000.0
balance = initial_balance
btc_holdings = 0.0

portfolio_values = []
buy_signals = []
sell_signals = []

print("Daily Ledger of Trades:")
print("-" * 50)

for i in range(len(df)):
    current_price = df['Price'].iloc[i]
    date_str = df['Date'].iloc[i].strftime('%Y-%m-%d')

    # Record the portfolio value at the start of the day
    current_portfolio_value = balance + btc_holdings * current_price
    portfolio_values.append(current_portfolio_value)

    # Skip moving average logic for the first 30 days
    if pd.isna(df['30-day MA'].iloc[i]) or i == 0 or pd.isna(df['7-day MA'].iloc[i-1]) or pd.isna(df['30-day MA'].iloc[i-1]):
        continue

    prev_7d_ma = df['7-day MA'].iloc[i-1]
    curr_7d_ma = df['7-day MA'].iloc[i]
    prev_30d_ma = df['30-day MA'].iloc[i-1]
    curr_30d_ma = df['30-day MA'].iloc[i]

    # Check for cross
    if prev_7d_ma <= prev_30d_ma and curr_7d_ma > curr_30d_ma:
        if balance > 0:
            btc_bought = balance / current_price
            btc_holdings += btc_bought
            print(f"{date_str}: BUY  {btc_bought:.6f} BTC at ${current_price:.2f}. Spent ${balance:.2f}.")
            balance = 0.0
            buy_signals.append((df['Date'].iloc[i], current_price))

    elif prev_7d_ma >= prev_30d_ma and curr_7d_ma < curr_30d_ma:
        if btc_holdings > 0:
            money_gained = btc_holdings * current_price
            balance += money_gained
            print(f"{date_str}: SELL {btc_holdings:.6f} BTC at ${current_price:.2f}. Received ${money_gained:.2f}.")
            btc_holdings = 0.0
            sell_signals.append((df['Date'].iloc[i], current_price))

df['Portfolio_Value'] = portfolio_values

print("-" * 50)
final_portfolio_value = balance + btc_holdings * df['Price'].iloc[-1]
print("Final Portfolio Performance:")
print(f"Initial Balance: ${initial_balance:.2f}")
print(f"Final Balance:   ${final_portfolio_value:.2f}")
print(f"Return:          {((final_portfolio_value - initial_balance) / initial_balance) * 100:.2f}%")

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Plot Stock Price and Moving Averages
ax1.plot(df['Date'], df['Price'], label='BTC Price', color='black', alpha=0.5)
ax1.plot(df['Date'], df['7-day MA'], label='7-day MA', color='blue', linestyle='--')
ax1.plot(df['Date'], df['30-day MA'], label='30-day MA', color='red', linestyle='-.')

# Plot Buy/Sell Signals
if buy_signals:
    buy_dates, buy_prices = zip(*buy_signals)
    ax1.scatter(buy_dates, buy_prices, marker='^', color='green', s=100, label='Buy Signal')
if sell_signals:
    sell_dates, sell_prices = zip(*sell_signals)
    ax1.scatter(sell_dates, sell_prices, marker='v', color='red', s=100, label='Sell Signal')

ax1.set_title('Simulated Bitcoin Price and Moving Averages')
ax1.set_ylabel('Price ($)')
ax1.legend()
ax1.grid(True)

# Plot Portfolio Returns
# Calculate percentage returns
df['Return_%'] = ((df['Portfolio_Value'] - initial_balance) / initial_balance) * 100
ax2.plot(df['Date'], df['Return_%'], label='Portfolio Return (%)', color='purple')
ax2.set_title('Portfolio Returns')
ax2.set_xlabel('Date')
ax2.set_ylabel('Return (%)')
ax2.axhline(0, color='black', linestyle='--', linewidth=1)
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('bitcoin_simulation_results.png')
print("Saved visualization to bitcoin_simulation_results.png")
