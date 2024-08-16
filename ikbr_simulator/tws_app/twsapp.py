from decimal import Decimal

from ibapi.client import *
from ibapi.common import TickAttribBidAsk
from ibapi.contract import ContractDetails
from ibapi.wrapper import *

from .twscommon import TWSCommon
from .contractdetails import TWSContractDetails
from .displaygroup import TWSDisplayGroup
from .tickbidask import TWSTickBidAsk
from .tradesim import TWSTradeSim


class TWSApp(EWrapper, EClient, TWSContractDetails, TWSDisplayGroup, TWSTradeSim, TWSTickBidAsk):
    
    def __init__(self):
        EClient.__init__(self, self)
        
        self.tws_common = TWSCommon()
        
        self.req_id_callback_map: dict[int, callable] = {}
        TWSContractDetails.__init__(self, self.tws_common)
        TWSDisplayGroup.__init__(self, self.tws_common)
        TWSTickBidAsk.__init__(self, self.tws_common)
        TWSTradeSim.__init__(self, self.tws_common)
    
    def nextValidId(self, orderId: int):
        self.tws_common.is_ready = True
        
    def tickByTickBidAsk(self, reqId: int, time_: int, bidPrice: float, askPrice: float, bidSize: Decimal, askSize: Decimal, tickAttribBidAsk: TickAttribBidAsk):
        return TWSTradeSim.process_bid_ask_tick(self, reqId, time_, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk)
    
    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        return TWSContractDetails.contractDetails(self, reqId, contractDetails)
    
    def contractDetailsEnd(self, reqId: int):
        return TWSContractDetails.contractDetailsEnd(self, reqId)
        
    def displayGroupUpdated(self, reqId: int, contractInfo: str):
        TWSDisplayGroup.displayGroupUpdated(self, reqId, contractInfo)

    def error(self, errorCode, reqId, errorString, placeholder=None):
        if errorCode > -1:
            self.tws_common.logger.error(f"Error code: {errorCode}, {reqId}, {errorString}")
        else:
            self.tws_common.logger.debug(f"TWSError: {errorCode}, {reqId}, {errorString}")
