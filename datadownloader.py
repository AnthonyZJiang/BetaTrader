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
        
get_intraday('SLRX', '1min', '2024-07-23', '2024-07-23', True)