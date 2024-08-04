import json
import time
from betatrader import FMP



with open('credential.json', 'r') as f:
    cred = json.load(f)
fmp = FMP(cred['api_key'])

t = time.perf_counter()
screener_result = fmp.get_stock_screener(priceMoreThan=1, priceLowerThan=20, isActivelyTrading="true", isFund="false", isEtf="false", limit= 10000, exchange="NASDAQ,NYSE,AMEX")
rt_result = fmp.get_full_real_time_price()
print(f"Time taken: {time.perf_counter() - t} seconds")
print('Number of screener:', len(screener_result))
print('Number of real time:', len(rt_result))
stocks = {}
for r in screener_result:
    if r['country'] == 'CN':
        continue
    if r['price'] < 1 or r['price'] > 20:
        continue
    stocks[r['symbol']] = [r['price'], r['volume']]

filtered_result = []
found_c = 0
t = time.perf_counter()
for r in rt_result:
    if r['lastSalePrice'] < 1 or r['lastSalePrice'] > 20:
        continue
    if r['volume'] < 100000:
        continue
    if r['bidSize'] < 0 and r['askSize'] > 0:
        continue
    if r['symbol'] not in stocks:
        continue
    found_c += 1
    if r['volume'] - stocks[r['symbol']][1] > 1000000:
        filtered_result.append(r)
print(f"Time taken: {time.perf_counter() - t} seconds") 
print('Number of results:', len(filtered_result))
print('Number of stocks found:', found_c)
