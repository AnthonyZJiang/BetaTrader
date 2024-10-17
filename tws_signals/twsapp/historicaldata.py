from ibapi.client import EClient
from ibapi.wrapper import *

from .twscommon import TWSCommon
from .datastore.histdatastore import HistDataStore


class TWSHistData():

    def __init__(self, tws_common: TWSCommon):
        self.tws_common = tws_common

    def request_historical_data(self, symbol: str):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "smart"
        contract.currency = "USD"
        self.reqHistoricalData(reqId=self.tws_common.hist_data_req_id, 
                          contract=contract,
                          endDateTime='', 
                          durationStr='1 D',
                          barSizeSetting='1 min',
                          whatToShow='Trades',
                          useRTH=0,                 #0 = Includes data outside of RTH | 1 = RTH data only 
                          formatDate=1,    
                          keepUpToDate=1,           #0 = False | 1 = True 
                          chartOptions=[])
        self.tws_common.hist_data_req_id_symbol_map[self.tws_common.hist_data_req_id] = symbol
        self.tws_common.hist_data_req_id += 1

    def cancel_tick_bid_ask(self, reqId):
        EClient.cancelTickByTickData(self, reqId)
        self.tws_common.hist_data_req_id_symbol_map.pop(reqId)
    
    def cancel_current_historical_data(self):
        if self.tws_common.hist_data_req_id - 1 in self.tws_common.hist_data_req_id_symbol_map:
            self.cancel_tick_bid_ask(self.tws_common.hist_data_req_id - 1)
            
    def historicalData(self, reqId, bar: BarData):
        symbol = self.tws_common.hist_data_req_id_symbol_map[reqId]
        if symbol not in self.tws_common.hist_data:
            self.tws_common.hist_data[symbol] = HistDataStore(symbol)
        self.tws_common.hist_data[symbol].add_data(bar)
        print(f"{symbol}: {bar.date} - {bar.high} - {bar.open} - {bar.close} - {bar.low} - {bar.volume}")
    
    def historicalDataUpdate(self, reqId: int, bar: BarData):
        symbol = self.tws_common.hist_data_req_id_symbol_map[reqId]
        if symbol not in self.tws_common.hist_data:
            self.tws_common.hist_data[symbol] = HistDataStore(symbol)
        self.tws_common.hist_data[symbol].add_data(bar)
        print(f"{symbol}: {bar.date} - {bar.high} - {bar.open} - {bar.close} - {bar.low} - {bar.volume}")
        return
    
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        symbol = self.tws_common.hist_data_req_id_symbol_map[reqId]
        print(f"End of historical data for {symbol}")
        return