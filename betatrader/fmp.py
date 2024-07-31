import requests
import json
import time
import logging
from .util.logging import setup_logger

def write_to_file(func):
    def _call_wrapper(*args, **kwargs):
        if 'filename' in kwargs:
            filename = kwargs.pop('filename')
            json_doc = func(*args, **kwargs)
            with open(filename, 'w') as f:
                json.dump(json_doc, f, indent=4)
        else:
            json_doc = func(*args, **kwargs)
        return json_doc
    return _call_wrapper

class FMP:
    """Financial Modeling Prep API"""    
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://financialmodelingprep.com/api/v3/'
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.logger = setup_logger('FMP', logging.DEBUG, logging.DEBUG)
        
    @write_to_file
    def get_historical_price_full(self, symbol):
        url = self._build_url('historical-price-full', symbol)
        return self._get_response(url)
    
    @write_to_file
    def get_emas(self, timeframe: str, symbol: str, period: int):
        url = self._build_url(['technical_indicator', timeframe, symbol],  ['type=ema', f'period={period}'])
        return self._get_response(url)
    
    @write_to_file
    def get_chart_intraday(self, symbol: str, interval: str, from_date: str, to_date: str, extended: bool = False):
        url = self._build_url(['historical-chart', interval, symbol],  [f'from={from_date}', f'to={to_date}', f'extended={"true" if extended else "false"}'])
        return self._get_response(url)
    
    @write_to_file
    def get_stock_screener(self, **kwargs):
        """Find stocks that meet your investment criteria with our Screener (Stock) endpoint.

        Args:
            kwargs: available parameters are marketCapMoreThan,  marketCapLowerThan, priceMoreThan, priceLowerThan, betaMoreThan, betaLowerThan,
            volumeMoreThan, volumeLowerThan, dividendMoreThan, dividendLowerThan, isEtf, isFund, isActivelyTrading, sector, industry, country, exchange, limit
        """
        if kwargs is None or len(kwargs) < 1:
            return None
        
        params = []
        for key, value in kwargs.items():
            if value:
                params.append(f'{key}={value}')
        
        url = self._build_url(['stock-screener'],  params)
        return self._get_response(url)
    
    def get_full_real_time_price(self):
        url = self._build_url(['stock','full','real-time-price'])
        return self._get_response(url)
 
    def _build_url(self, path_params: list | str, query_params: list | str = []) -> str:
        if isinstance(path_params, list):
            path_params = '/'.join(path_params)
        api = 'apikey=' + self.api_key
        if query_params is None:
            query_params = api
        elif isinstance(query_params, list):
            query_params.append(api)
            query_params = '&'.join(query_params)
        else:
            query_params += '&' + api
        url = self.base_url + path_params + '?' + query_params
        return url
    
    def _get_response(self, url):
        self.logger.info(f"Requesting {url}")
        start = time.perf_counter()
        response = requests.get(url, self.headers)
        self.logger.debug(f"Request took: {(time.perf_counter() - start):3f} seconds")
        return response.json()
