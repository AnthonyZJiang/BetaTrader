# Micro pullback
Patterns:
- close_price < open_price
- volume < max(Volumes since the trend)
- duration <= 2 candles
- close_price > max(open_price of green candles since the trend)
- close_price > close_price of previous green - 0.1
When to buy:
- price > max(open of red candles)
Set stop limit:
- price <= min(close of red candles)

# Bull flag
Patterns:
- duration == 4 candles
- volume < max(Volumes since the trend)
When to buy:
- price > max(open of red candles)
Set stop limit:
- price <= min(close of red candles)

# Consolidation
Patterns:
**1 min chart**
- close_price > EMA9 - 0.1
- close_price > close_price of trend * 0.8
**5 min chart**
- bull flag pattern *or* micro pull back pattern

When to buy:
**1 min chart**
- EMA9 > EMA20
- MACD > signal

# Exit signals
- EMA 9 < EMA20