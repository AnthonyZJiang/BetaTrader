from betatrader.trendanalyser.common.maths import *
from betatrader.trendanalyser.common.kline import KlineBar

MACD_CROSS_TOLERANCE = 0.01

class MACDAnalyser:
    
    def __init__(self, fast_period = 12, slow_period = 26, signal_period = 9) -> None:
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, kline: list[KlineBar]):
        bar = kline[-1]
        prev_tick = kline[-2] if len(kline) > 1 else bar
        bar.macd_fast_ema = ema(bar.close_price, prev_tick.macd_fast_ema, self.fast_period)
        bar.macd_slow_ema = ema(bar.close_price, prev_tick.macd_slow_ema, self.slow_period)
        bar.macd_curve = bar.macd_fast_ema - bar.macd_slow_ema
        bar.macd_signal = ema(bar.macd_curve, prev_tick.macd_curve, self.signal_period)
        bar.macd = bar.macd_curve - bar.macd_signal
        if not bar.macd_good and bar.macd > - MACD_CROSS_TOLERANCE:
            bar.macd_good = True
            bar.macd_golden_cross = True
            return
        if bar.macd_good and bar.macd <= MACD_CROSS_TOLERANCE:
            bar.macd_good = False
            bar.macd_death_cross = True