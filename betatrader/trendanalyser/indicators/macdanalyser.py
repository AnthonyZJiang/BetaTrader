from betatrader.maths import *
from betatrader.trendanalyser.kline import KlineTick

MACD_CROSS_TOLERANCE = 0.01

class MACDAnalyser:
    
    def __init__(self, fast_period = 12, slow_period = 26, signal_period = 9) -> None:
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, kline: list[KlineTick]):
        tick = kline[-1]
        prev_tick = kline[-2] if len(kline) > 1 else tick
        tick.macd_fast_ema = ema(tick.close_price, prev_tick.macd_fast_ema, self.fast_period)
        tick.macd_slow_ema = ema(tick.close_price, prev_tick.macd_slow_ema, self.slow_period)
        tick.macd_curve = tick.macd_fast_ema - tick.macd_slow_ema
        tick.macd_signal = ema(tick.macd_curve, prev_tick.macd_curve, self.signal_period)
        tick.macd = tick.macd_curve - tick.macd_signal
        if not tick.macd_good and tick.macd > - MACD_CROSS_TOLERANCE:
            tick.macd_good = True
            tick.macd_golden_cross = True
            return
        if tick.macd_good and tick.macd <= MACD_CROSS_TOLERANCE:
            tick.macd_good = False
            tick.macd_death_cross = True