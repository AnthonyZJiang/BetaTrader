from ibapi.client import *
from ibapi.wrapper import *

from .historicaldata import HistoricalDataExt
from .scanner import Scanner


class TWSApp(EWrapper, EClient, Scanner, HistoricalDataExt):
    def __init__(self):
        EClient.__init__(self, self)
        Scanner.__init__(self)
        HistoricalDataExt.__init__(self)
        self.disable_error = False
        self.histdata_req_id_lookup = {}  # type: dict[int, int] # req_id: rank

    def nextValidId(self, orderId: int):
        self.request_scanner(self.request_data_at_scanner_end)

    def request_data_at_scanner_end(self):
        self.histdata_req_id_lookup = {}
        for re in self.scanner_results:
            # request day data
            id = self.request_historical_data(re.symbol, "2 D", "1 day", 1)
            self.histdata_req_id_lookup[id] = re.rank
            # request min data for the last 30 minutes
            id = self.request_historical_data(re.symbol, "1800 S", "1 min", 1)
            self.histdata_req_id_lookup[id] = re.rank
        self.scanner_results = {}

    def historicalData(self, reqId: int, bar: BarData):
        return HistoricalDataExt.historicalData(self, reqId, bar)

    def historicalDataUpdate(self, reqId: int, bar: BarData):
        return HistoricalDataExt.historicalDataUpdate(self, reqId, bar)

    def scannerData(self, reqId: int, rank: int, contractDetails: ContractDetails, distance: str, benchmark: str, projection: str, legsStr: str):
        return Scanner.scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr)

    def scannerDataEnd(self, reqId: int):
        return Scanner.scannerDataEnd(self, reqId)

    def error(self, errorCode, reqId, errorString, placeholder):
        if not self.disable_error:
            super().error(reqId, errorCode, errorString)
            pass
