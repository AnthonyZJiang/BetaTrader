import json
import pathlib
import logging
import datetime
from betatrader import FMP
from betatrader.util.logging import setup_logger


MAX_DAYS = 10
PRICE_CAP = 20
FILE_NAME = 'stock_records.json'

logger = setup_logger('StockScreener', logging.DEBUG, logging.DEBUG)

def get_new_stock_record():
    stocks = {}
    stock_records = {
        'first_record_datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'number_of_stocks': 0,
        'stocks': stocks
    }
    return stock_records

def get_existing_stock_record():
    if not pathlib.Path(FILE_NAME).exists():
        return None
    with open(FILE_NAME, 'r') as f:
        stock_records = json.load(f)
        
    n = len(stock_records['stocks'])
    if n != stock_records['number_of_stocks']:
        logger.error(f"Number of stocks in record, mismatch: {n} != {stock_records['number_of_stocks']}")
        user_input = input("Stock record is corrupted. Do you want to create a new one? (y/n): ")
        if user_input.lower() == 'y':
            return None
        else:
            exit()
    
    updated_date = datetime.datetime.strptime(stock_records['updated_datetime'], '%Y-%m-%d %H:%M:%S')
    if (datetime.datetime.now() - updated_date).days == 0:
        user_input = input("Stock record is up to date. Do you want to update it? (y/n): ")
        if user_input.lower() == 'n':
            exit()
    
    logger.info("Stock record loaded.")
    logger.info(f"Number of existing stocks in record: {n}")

def main(cred):
    fmp = FMP(cred['api_key'])
    new_record = False
    
    stock_records = get_existing_stock_record()
    if stock_records is None:
        stock_records = get_new_stock_record()
        new_record = True
        
    stocks = stock_records['stocks'] # type: dict[str, list[list[int, float, float]]]
    first_record_date = datetime.datetime.strptime(stock_records['first_record_datetime'], '%Y-%m-%d %H:%M:%S')
    days_since_first = (datetime.datetime.now() - first_record_date).days
        
    screener_result = fmp.get_stock_screener(priceLowerThan=PRICE_CAP, isActivelyTrading="true", isFund="false", isEtf="false", limit= 10000, exchange="NASDAQ,NYSE,AMEX")
    logger.info(f"Number of screener results: {len(screener_result)}")

    if not screener_result or not len(screener_result) > 0:
        return

    for r in screener_result:
        if r['country'] == 'CN':
            continue
        record = [days_since_first, r['price'], r['volume']]
        if not new_record and r['symbol'] in stocks:
            if stocks[r['symbol']][-1][0] == days_since_first:
                # same day, update the existing record.
                stocks[r['symbol']][-1] = record
                continue
            if len(stocks[r['symbol']]) > MAX_DAYS:
                # max records reached for this symbol, remove the oldest
                stocks[r['symbol']].pop(0)
            stocks[r['symbol']].append(record)
        else:
            # new record or new symbol
            stocks[r['symbol']] = record
    logger.info(f"Number of stocks in record, after update: {len(stocks)}")
        
    stock_records['updated_datetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    stock_records['number_of_stocks'] = len(stocks)
    with open(FILE_NAME, 'w') as f:
        json.dump(stock_records, f, indent=4)
    logger.info("Stock record saved.")
        
if __name__ == '__main__':
    with open('credential.json', 'r') as f:
        cred = json.load(f)
    main(cred)