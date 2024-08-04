import json
import time
import logging
import numpy as np
from pathlib import Path
from betatrader import FMP
from betatrader.util.logging import setup_logger


with open('credential.json', 'r') as f:
    cred = json.load(f)
fmp = FMP(cred['api_key'])

logger = setup_logger('StockScanner', logging.DEBUG, logging.DEBUG)
if not Path('stock_records.json').exists():
    exit()
    
with open('stock_records.json', 'r') as f:
    stock_records = json.load(f)

stocks = stock_records['stocks']

def scan(stocks):
    rt_result = fmp.get_full_real_time_price()

    filtered_result = []
    for r in rt_result:
        if r['lastSalePrice'] < 1 or r['lastSalePrice'] > 20:
            continue
        if r['volume'] < 100000:
            continue
        if r['bidSize'] <= 0 and r['askSize'] <= 0:
            continue
        if r['symbol'] not in stocks:
            continue
        last_price = stocks[r['symbol']][-1][1]
        last_volume = stocks[r['symbol']][-1][3]
        if (r['price'] - last_price) / last_price > 0.1 and (r['volume'] - last_volume) / last_volume < 0.2:
            filtered_result.append(r)
