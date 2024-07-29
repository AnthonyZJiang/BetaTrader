from betatrader.maths import *
from betatrader.trendanalyser.kline import KlineTick

EMA_CROSS_TOLERANCE = 0.01

class EMAAnalyser:
    
    def __init__(self, fast_period = 9, slow_period = 20) -> None:
        self.fast_period = fast_period
        self.slow_period = slow_period

    def calculate(self, kline: list[KlineTick]):
        tick = kline[-1]
        prev_tick = kline[-2] if len(kline) > 1 else tick
        tick.fast_ema = ema(tick.close_price, prev_tick.fast_ema, self.fast_period)
        tick.slow_ema = ema(tick.close_price, prev_tick.slow_ema, self.slow_period)
        if not tick.ema_good and tick.fast_ema + EMA_CROSS_TOLERANCE > tick.slow_ema:
            tick.ema_good = True
            tick.ema_golden_cross = True
            return
        if tick.ema_good and tick.fast_ema - EMA_CROSS_TOLERANCE <= tick.slow_ema:
            tick.ema_good = False
            tick.ema_death_cross = True