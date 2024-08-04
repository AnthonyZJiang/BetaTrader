from queue import Queue

from ibapi.client import BarData
from ibapi.contract import Contract

DEFAULT_REQ_ID_HIST_DATA = 4001


class HistoricalDataRequest:
    req_id = DEFAULT_REQ_ID_HIST_DATA

    def __init__(self, symbol: str, duration: str, interval: str, keep_update: bool):
        self.symbol: str = symbol
        self.req_id: int = HistoricalDataRequest.req_id
        self.duration: str = duration  # 1 D, 2 D, 1800 S
        self.interval: str = interval  # 1 day, 1 min
        self.keep_update: bool = keep_update

        HistoricalDataRequest.req_id += 1
        if HistoricalDataRequest.req_id > 4999:
            HistoricalDataRequest.req_id = DEFAULT_REQ_ID_HIST_DATA


class HistoricalDataStore:
    def __init__(self, request_obj: HistoricalDataRequest, bar: BarData):
        self.bar: BarData = bar
        self.req_id: int = request_obj.req_id
        self.symbol: str = request_obj.symbol
        self.duration: str = request_obj.duration
        self.interval: str = request_obj.interval


class HistoricalDataExt():
    def __init__(self) -> None:
        self.histdata_requests: dict[int, HistoricalDataRequest] = {}
        self.received_histdata: Queue[HistoricalDataStore] = Queue()

    def request_historical_data(self, symbol, duration_str, interval_str, keep_update) -> int:
        contract = self._make_contract(symbol)
        req = HistoricalDataRequest(
            symbol, duration_str, interval_str, keep_update)
        self.reqHistoricalData(req.req_id, contract, "", duration_str,
                               interval_str, "Trades", 0, 1, keep_update, [])
        self.histdata_requests[req.req_id] = req
        return req.req_id

    def cancel_historical_data(self, req_id) -> None:
        self.cancelHistoricalData(req_id)
        del self.histdata_requests[req_id]

    def cancel_all_historical_data(self) -> None:
        for req_id in self.histdata_requests:
            if not self.histdata_requests[req_id].keep_update:
                continue
            self.cancelHistoricalData(req_id)
        self.histdata_requests = {}

    def historicalData(self, reqId: int, bar: BarData) -> None:
        self.received_histdata.put(HistoricalDataStore(
            self.histdata_requests[reqId], bar))

    def historicalDataUpdate(self, reqId: int, bar: BarData) -> None:
        self.received_histdata.put(HistoricalDataStore(
            self.histdata_requests[reqId], bar))

    def _make_contract(self, symbol: str) -> Contract:
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        return contract
