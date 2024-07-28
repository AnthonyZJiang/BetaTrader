#!/usr/bin/env python
import json
import pandas as pd
from urllib.request import urlopen
import certifi

def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

def filter_stocks(api_key):
    base_url = "https://financialmodelingprep.com/api/v3/stock-screener"
    params = {
        "priceMoreThan": 2,
        "priceLowerThan": 20,
        "marketCapLowerThan": 50000000000,  # setting a high cap to include all small cap stocks
        "exchange": "nasdaq,nyse,amex",
        "apikey": api_key
    }
    
    url = (f"{base_url}?priceMoreThan={params['priceMoreThan']}&priceLowerThan={params['priceLowerThan']}&"
           f"marketCapLowerThan={params['marketCapLowerThan']}&exchange={params['exchange']}&apikey={params['apikey']}")
    data = get_jsonparsed_data(url)
    
    filtered_stocks = []

    for stock in data:
        symbol = stock["symbol"]
        float_url = f"https://financialmodelingprep.com/api/v4/shares_float?symbol={symbol}&apikey={api_key}"
        float_data = get_jsonparsed_data(float_url)

        if float_data:
            float_shares = float_data[0]["floatShares"]
            if isinstance(float_shares, str):
                float_shares = float(float_shares)
            if float_shares <= 20000000:
                filtered_stocks.append({
                    "symbol": stock["symbol"],
                    "companyName": stock.get("companyName", ""),
                    "marketCap": stock.get("marketCap", 0),
                    "sector": stock.get("sector", ""),
                    "industry": stock.get("industry", ""),
                    "beta": stock.get("beta", 0),
                    "price": stock.get("price", 0),
                    "lastAnnualDividend": stock.get("lastAnnualDividend", 0),
                    "volume": stock.get("volume", 0),
                    "exchange": stock.get("exchange", ""),
                    "exchangeShortName": stock.get("exchangeShortName", ""),
                    "country": stock.get("country", ""),
                    "isEtf": stock.get("isEtf", False),
                    "isFund": stock.get("isFund", False),
                    "isActivelyTrading": stock.get("isActivelyTrading", False)
                })
    
    return filtered_stocks

def save_to_csv(stocks, filename='filtered_stocks.csv'):
    df = pd.DataFrame(stocks)
    df.to_csv(filename, index=False)
    print(f"Filtered stocks saved to {filename}")

def main():
    api_key = 'fZrnj5liq7qbvkdv0G5bKIUUS2HEiLMJ'
    filtered_stocks = filter_stocks(api_key)
    save_to_csv(filtered_stocks)

if __name__ == "__main__":
    main()
