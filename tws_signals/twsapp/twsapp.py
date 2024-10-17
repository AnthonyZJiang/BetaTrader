from ibapi.client import *
from ibapi.scanner import ScannerSubscription
from ibapi.wrapper import *
from ibapi.tag_value import TagValue

from rich import table, console
import time

from .twscommon import TWSCommon
from .historicaldata import TWSHistData
from .displaygroup import TWSDisplayGroup


class TWSApp(EWrapper, EClient, TWSHistData, TWSDisplayGroup):
    
    def __init__(self):
        EClient.__init__(self, self)
        
        self.tws_common = TWSCommon()
        
        self.req_id_callback_map: dict[int, callable] = {}
        TWSHistData.__init__(self, self.tws_common)
        TWSDisplayGroup.__init__(self, self.tws_common)
        self.console = console.Console()
        
    
    def nextValidId(self, orderId: int):
        self.tws_common.is_ready = True
        self.request_historical_data("RILY")
        print(f"NextValidId: {orderId}")
    
    def historicalData(self, reqId, bar):
        return TWSHistData.historicalData(self, reqId, bar)
    
    def historicalDataUpdate(self, reqId: int, bar: BarData):
        return TWSHistData.historicalDataUpdate(self, reqId, bar)
    
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        return TWSHistData.historicalDataEnd(self, reqId, start, end)
    
    def displayGroupUpdated(self, reqId: int, contractInfo: str):
        TWSDisplayGroup.displayGroupUpdated(self, reqId, contractInfo)

    # def error(self, errorCode, reqId, errorString, placeholder=None):
    #     if errorCode > -1:
    #         self.tws_common.logger.error(f"Error code: {errorCode}, {reqId}, {errorString}")
    #     else:
    #         self.tws_common.logger.debug(f"TWSError: {errorCode}, {reqId}, {errorString}")
