import numpy as np
import pandas as pd

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

print("Daily Ledger of Trades:")
print("-" * 50)

for i in range(1, len(df)):
    if pd.isna(df['30-day MA'].iloc[i]) or pd.isna(df['7-day MA'].iloc[i-1]) or pd.isna(df['30-day MA'].iloc[i-1]):
        continue

    prev_7d_ma = df['7-day MA'].iloc[i-1]
    curr_7d_ma = df['7-day MA'].iloc[i]
    prev_30d_ma = df['30-day MA'].iloc[i-1]
    curr_30d_ma = df['30-day MA'].iloc[i]

    current_price = df['Price'].iloc[i]
    date_str = df['Date'].iloc[i].strftime('%Y-%m-%d')

    # Check for cross
    if prev_7d_ma <= prev_30d_ma and curr_7d_ma > curr_30d_ma:
        if balance > 0:
            btc_bought = balance / current_price
            btc_holdings += btc_bought
            print(f"{date_str}: BUY  {btc_bought:.6f} BTC at ${current_price:.2f}. Spent ${balance:.2f}.")
            balance = 0.0

    elif prev_7d_ma >= prev_30d_ma and curr_7d_ma < curr_30d_ma:
        if btc_holdings > 0:
            money_gained = btc_holdings * current_price
            balance += money_gained
            print(f"{date_str}: SELL {btc_holdings:.6f} BTC at ${current_price:.2f}. Received ${money_gained:.2f}.")
            btc_holdings = 0.0

print("-" * 50)
final_portfolio_value = balance + btc_holdings * df['Price'].iloc[-1]
print("Final Portfolio Performance:")
print(f"Initial Balance: ${initial_balance:.2f}")
print(f"Final Balance:   ${final_portfolio_value:.2f}")
print(f"Return:          {((final_portfolio_value - initial_balance) / initial_balance) * 100:.2f}%")
