import json
from betatrader import FMP

with open('credential.json', 'r') as f:
    cred = json.load(f)
fmp = FMP(cred['api_key'])

def get_intraday(symbol, interval, date_from, date_to, extended):
    data = fmp.get_chart_intraday(symbol, interval, date_from, date_to, extended)
    with open(f'data/{symbol}_{interval}_{date_from}{"_extended" if extended else ""}.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("Data saved")
        
get_intraday('AMZN', '1day', '2010-01-01', '2024-08-03', False)