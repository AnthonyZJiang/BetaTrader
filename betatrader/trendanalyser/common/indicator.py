from .kline import KlineBar
from .maths import *
from .datatype import *

class MACDCalculator:
    MACD_CROSS_TOLERANCE = 0.01
    
    def __init__(self, fast_period = 12, slow_period = 26, signal_period = 9) -> None:
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, kline: list[KlineBar]):
        bar = kline[-1]
        this_idct = MACDData()
        bar.indicators["macd"] = this_idct
        
        prev_bar = kline[-2] if len(kline) > 1 else bar
        if "macd" not in prev_bar.indicators:
            raise Exception("MACD data not found in previous bar")
        prev_idct = prev_bar.indicators["macd"]
        assert(isinstance(prev_idct, MACDData))

        this_idct.fast_ema = ema(bar.data.close, prev_idct.fast_ema, self.fast_period)
        this_idct.slow_ema = ema(bar.data.close, prev_idct.slow_ema, self.slow_period)
        this_idct.curve = this_idct.fast_ema - this_idct.slow_ema
        this_idct.signal = ema(this_idct.curve, prev_idct.curve, self.signal_period)
        this_idct.macd = this_idct.curve - this_idct.signal
        if not prev_idct.good and this_idct.macd > - MACDCalculator.MACD_CROSS_TOLERANCE:
            this_idct.good = True
            this_idct.golden_cross = True
            return
        if this_idct.good and this_idct.macd <= MACDCalculator.MACD_CROSS_TOLERANCE:
            this_idct.good = False
            this_idct.death_cross = True
            

class EMACalculator:
    EMA_CROSS_TOLERANCE = 0.01
    
    def __init__(self, periods: list[int]) -> None:
        # sort the periods in ascending order
        self.periods = periods
        self.periods.sort()
        self.n = len(self.periods)

    def calculate(self, kline: list[KlineBar]):
        bar = kline[-1]
        this_idct = EMAData()
        bar.indicators["ema"] = this_idct
        
        prev_bar = kline[-2] if len(kline) > 1 else bar
        if "ema" not in prev_bar.indicators:
            raise Exception("EMA data not found in previous bar")
        prev_idct = prev_bar.indicators["ema"]
        assert(isinstance(prev_idct, EMAData))

        this_idct.prev_values = prev_idct.values
        for period in self.periods:
            if period not in prev_idct.values:
                prev_idct.values[period] = bar.data.close
            this_idct.values[period] = ema(bar.data.close, prev_idct.values[period], period)
        
        this_idct.good = True
        for i in range(self.n - 1):
            this_idct.good &= this_idct.values[self.periods[i]] > this_idct.values[self.periods[i+1]]
            

class RSICalculator:
    def __init__(self, periods: list[int] | None = None) -> None:
        # sort the periods in ascending order
        if periods is None:
            self.periods = [6,12,24]
        else:
            self.periods = periods
            self.periods.sort()
        self.n = len(self.periods)

    def calculate(self, kline: list[KlineBar]):
        bar = kline[-1]
        this_idct = RSIData()
        bar.indicators["rsi"] = this_idct
        
        prev_bar = kline[-2] if len(kline) > 1 else bar
        if "rsi" not in prev_bar.indicators:
            raise Exception("RSI data not found in previous bar")
        prev_idct = prev_bar.indicators["rsi"]
        assert(isinstance(prev_idct, RSIData))

        for period in self.periods:
            delta = bar.data.close - prev_bar.data.close
            gain = max(delta, 0)
            diff = abs(delta)
            if period not in prev_idct.values:
                prev_idct.gains[period] = gain
                prev_idct.diffs[period] = diff
            avg_gain = sma(gain, prev_idct.gains[period], period, 1)
            avg_diff = sma(diff, prev_idct.diffs[period], period, 1)
            if avg_diff == 0:
                rsi = 100 if avg_gain > 0 else 0
            else:
                rsi = avg_gain / avg_diff * 100
            this_idct.values[period] = rsi
            this_idct.gains[period] = avg_gain
            this_idct.diffs[period] = avg_diff
            
            
class KDJCalculator:
    def __init__(self, rsv_period = 9, k_period =3 , d_period = 3) -> None:
        self.rsv_period = rsv_period
        self.k_period = k_period
        self.d_period = d_period
        
    def calculate(self, kline: list[KlineBar]):
        bar = kline[-1]
        this_idct = KDJData()
        bar.indicators["kdj"] = this_idct
        
        prev_bar = kline[-2] if len(kline) > 1 else bar
        if "kdj" not in prev_bar.indicators:
            raise Exception("KDJ data not found in previous bar")
        prev_idct = prev_bar.indicators["kdj"]
        assert(isinstance(prev_idct, KDJData))

        this_idct.lows = prev_idct.lows.copy()
        this_idct.highs = prev_idct.highs.copy()
        low, high = self._add_low_high(bar, this_idct)
        
        this_idct.rsv = (bar.data.close - low) / (high - low) * 100
        this_idct.k = 2/3 * prev_idct.k + 1/3 * this_idct.rsv
        this_idct.d = 2/3 * prev_idct.d + 1/3 * this_idct.k
        this_idct.j = 3 * this_idct.k - 2 * this_idct.d
        
    def _add_low_high(self, bar: KlineBar, kdj: KDJData):
        if len(kdj.lows) == self.rsv_period:
            kdj.lows.pop(0)
        if len(kdj.highs) == self.rsv_period:
            kdj.highs.pop(0)
        kdj.lows.append(bar.data.low)
        kdj.highs.append(bar.data.high)
        return min(kdj.lows), max(kdj.highs)