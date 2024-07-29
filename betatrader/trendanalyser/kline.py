import numpy as np


class KlineTick:
    
    def __init__(self, data, index):
        self.data = data
        self.index = index
        
        self.open_price = data['open']
        self.close_price = data['close']
        self.high_price = data['high']
        self.low_price = data['low']
        self.volume = data['volume']
        
        # Analytic
        self.is_green = self.close_price > self.open_price
        self.is_red = not self.is_green
        self.direction = 1 if self.is_green else -1
        self.candle_body_low = min ([self.close_price, self.open_price])
        self.candle_body_high = max([self.close_price, self.open_price])
        
        # Trend
        self.highest = self.candle_body_high
        self.highest_since = 0
        self.lowest = self.candle_body_low
        self.lowest_since = 0
        
        # Volume
        self.volume_ema = 0
        
        # EMA
        self.fast_ema = 0
        self.slow_ema = 0
        self.ema_golden_cross = False
        self.ema_death_cross = False
        self.ema_good = False
        
        # MACD
        self.macd_fast_ema = 0
        self.macd_slow_ema = 0
        self.macd = 0
        self.macd_signal = 0
        self.macd_curve = 0
        self.macd_golden_cross = False
        self.macd_death_cross = False
        self.macd_good = False
        
        # Pattern
        self.micro_pullback_likelihood = 0
        
        # Signals
        self.entry_signal = np.nan
        self.exit_signal = np.nan
        self.reason = None

class KlineTickGroup:
    
    def __init__(self, tick: KlineTick = None) -> None:
        self.count = 0
        if tick is None:
            return
        self._add_first_tick(tick)
        
    def _add_first_tick(self, tick: KlineTick):
        self.direction = 1 if tick.is_green else -1
        self.directions = [tick.direction]
        self.is_up = self.direction == 1
        self.is_down = self.direction == -1
        
        self.start_index = tick.index
        self.end_index = tick.index
        self.count = 1
        
        self.volume = tick.volume
        self.high = tick.high_price
        self.low = tick.low_price
        self.body_high = tick.candle_body_high
        self.body_low = tick.candle_body_low
        self.range = self.body_high - self.body_low
        
        self.tick_max_volume = tick.volume
        
        self.open = tick.open_price
        self.close = tick.close_price
        
    def add_tick(self, tick: KlineTick):
        if self.count == 0:
            self._add_first_tick(tick)
            return
        if tick.direction != 0 and tick.direction != self.direction:
            tick.direction = 0
            self.is_up = False
            self.is_down = False
        self.directions.append(tick.direction)
        self.count += 1
        self.volume += tick.volume
        self.end_index = tick.index
        self.high = max(self.high, tick.high_price)
        self.low = min(self.low, tick.low_price)
        self.body_high = max(self.body_high, tick.candle_body_high)
        self.body_low = min(self.body_low, tick.candle_body_low)
        self.tick_max_volume = max(self.tick_max_volume, tick.volume)
        self.range = self.body_high - self.body_low
        self.close = tick.close_price
        
    def get_candles(self, kline: list[KlineTick]):
        return kline[self.start_index:self.end_index+self.count]