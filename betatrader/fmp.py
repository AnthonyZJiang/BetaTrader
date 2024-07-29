import requests
import json

def write_to_file(func):
    def _call_wrapper(*args, **kwargs):
        if filename := kwargs.pop('filename'):
            response = func(*args, **kwargs)
            with open(filename, 'w') as f:
                json.dump(response, f, indent=4)
        return response
    return _call_wrapper

class FMP:
    """Financial Modeling Prep API"""    
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://financialmodelingprep.com/api/v3/'
        self.headers = {
            'Content-Type': 'application/json'
        }
        
    @write_to_file
    def get_historical_price_full(self, symbol):
        url = self.construct_url('historical-price-full', symbol)
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    @write_to_file
    def get_emas(self, timeframe: str, symbol: str, period: int):
        url = self.construct_url(['technical_indicator', timeframe, symbol],  ['type=ema', f'period={period}'])
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    @write_to_file
    def get_chart_intraday(self, symbol: str, interval: str, from_date: str, to_date: str, extended: bool = False):
        url = self.construct_url(['historical-chart', interval, symbol],  [f'from={from_date}', f'to={to_date}', f'extended={"true" if extended else "false"}'])
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    @write_to_file
    def get_scanner(self, **kwargs):
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
        
        url = self.construct_url(['stock-screener'],  params)
        response = requests.get(url, headers=self.headers)
        return response.json()
 
    def construct_url(self, path_params: list | str, query_params: list | str) -> str:
        if isinstance(path_params, list):
            path_params = '/'.join(path_params)
        if isinstance(query_params, list):
            query_params = '&'.join(query_params)
        url = self.base_url + path_params + '?' + query_params + '&apikey=' + self.api_key
        return url