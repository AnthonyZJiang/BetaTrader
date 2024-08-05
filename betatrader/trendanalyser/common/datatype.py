class BarData:
    def __init__(self, data):
        self.open = data['open']
        self.close = data['close']
        self.high = data['high']
        self.low = data['low']
        self.volume = data['volume']
        

class MACDData:
    def __init__(self) -> None:
        self.fast_ema = 0
        self.slow_ema = 0
        self.curve = 0
        self.signal = 0
        self.macd = 0
        self.good = False
        self.golden_cross = False
        self.death_cross = False
        
        
class EMAData:
    def __init__(self) -> None:
        self.values: dict[int, int] = {}
        self.prev_values: dict[int, int] = {}
        self.good = False
        
        
class RSIData:
    def __init__(self) -> None:
        self.values: dict[int, int] = {}
        self.prev_values: dict[int, int] = {}
        self.gains: dict[int, int] = {}
        self.diffs: dict[int, int] = {}
        
        
class KDJData:
    def __init__(self) -> None:
        self.k = 50
        self.d = 50
        self.j = 0
        self.rsv = 0
        self.lows = []
        self.highs = []
