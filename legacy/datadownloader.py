import json
from betatrader import FMP

with open('credential.json', 'r') as f:
    cred = json.load(f)
fmp = FMP(cred['api_key'])


# Scanner
fmp.get_stock_screener(filename="scanner_result.json", priceMoreThan=1, priceLowerThan=20, limit=1000000, isActivelyTrading="true", isFund="false", isEtf="false")

# Intraday
symbol = "SLRX"
interval = "1min"
date_from = "2024-07-23"
date_to = "2024-07-23"
extended = True
filename = f'data/{symbol}_{interval}_{date_from}{"extended" if extended else ""}.json'
fmp.get_chart_intraday(symbol, interval, date_from, date_to, extended, filename=filename)
