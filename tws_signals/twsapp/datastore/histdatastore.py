from ibapi.wrapper import BarData

class HistDataStore:
    
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.timestamp = []
        self.high = []
        self.low = []
        self.open = []
        self.close = []
        self.volume = []
    
    def add_data(self, bar: BarData):
        if len(self.timestamp) > 0 and bar.date == self.timestamp[-1]:
            self.high[-1] = bar.high
            self.low[-1] = bar.low
            self.open[-1] = bar.open
            self.close[-1] = bar.close
            self.volume[-1] = bar.volume
            return
        self.timestamp.append(bar.date)
        self.high.append(bar.high)
        self.low.append(bar.low)
        self.open.append(bar.open)
        self.close.append(bar.close)
        self.volume.append(bar.volume)