import json
import requests
# https://financialmodelingprep.com/api/v3/technical_indicator/1day/AAPL?type=ema&period=26&apikey=KQ6mApbASvNcJoXu8ITWcih4sPuURH9a


class FMP:
    """Financial Modeling Prep API"""    
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://financialmodelingprep.com/api/v3/'
        self.headers = {
            'Content-Type': 'application/json'
        }
        
    def get_historical_price_full(self, symbol):
        url = self.construct_url('historical-price-full', symbol)
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_emas(self, timeframe: str, symbol: str, period: int):
        url = self.construct_url(['technical_indicator', timeframe, symbol],  ['type=ema', f'period={period}'])
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def construct_url(self, path_params: list | str, query_params: list | str) -> str:
        if isinstance(path_params, list):
            path_params = '/'.join(path_params)
        if isinstance(query_params, list):
            query_params = '&'.join(query_params)
        url = self.base_url + path_params + '?' + query_params + '&apikey=' + self.api_key
        return url