from betatrader.trendanalyser.common.maths import *
from betatrader.trendanalyser.common.kline import KlineBar

EMA_CROSS_TOLERANCE = 0.01

class EMAAnalyser:
    
    def __init__(self, fast_period = 9, slow_period = 20) -> None:
        self.fast_period = fast_period
        self.slow_period = slow_period

    def calculate(self, kline: list[KlineBar]):
        bar = kline[-1]
        prev_tick = kline[-2] if len(kline) > 1 else bar
        bar.fast_ema = ema(bar.close_price, prev_tick.fast_ema, self.fast_period)
        bar.slow_ema = ema(bar.close_price, prev_tick.slow_ema, self.slow_period)
        if not bar.ema_good and bar.fast_ema + EMA_CROSS_TOLERANCE > bar.slow_ema:
            bar.ema_good = True
            bar.ema_golden_cross = True
            return
        if bar.ema_good and bar.fast_ema - EMA_CROSS_TOLERANCE <= bar.slow_ema:
            bar.ema_good = False
            bar.ema_death_cross = True