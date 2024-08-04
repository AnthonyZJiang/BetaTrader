from ibapi.tag_value import TagValue
from ibapi.scanner import ScannerSubscription
from ibapi.contract import ContractDetails


class ScannerDataStore:
    def __init__(self, symbol: str, rank: int):
        self.symbol = symbol
        self.rank = rank


class Scanner:
    def __init__(self):
        self.scanner_data_ready = False
        self.scanner_results: list[ScannerDataStore] = []
        self.scanner_end_callback = None

    def nextValidId(self, orderId: int):
        print("id", orderId)
        self.request_scanner()

    def request_scanner(self, callback):
        scanner_sub = ScannerSubscription()

        tag_values = [
            TagValue('priceAbove', 1),
            TagValue('priceBelow', 20),
            TagValue('stVolume3minAbove', 10000),
            TagValue('changePercAbove', 10)]

        scanner_sub.instrument = "STK"
        scanner_sub.locationCode = "STK.US"
        scanner_sub.scanCode = "TOP_PERC_GAIN"

        self.reqScannerSubscription(7001, scanner_sub, [], tag_values)
        self.scanner_end_callback = callback

    def scannerData(self, reqId: int, rank: int, contractDetails: ContractDetails, distance: str, benchmark: str, projection: str, legsStr: str):
        self.scanner_data_ready = False
        self.scanner_results.append(ScannerDataStore(
            contractDetails.contract.symbol, rank))

    def scannerDataEnd(self, reqId: int):
        if callable(self.scanner_end_callback):
            self.scanner_end_callback()
        self.scanner_data_ready = True
