import numpy as np
from .datatype import *


class KlineBar:
    
    def __init__(self, data, index):
        self.index = index
        self.data = BarData(data)
        self.date = data['date']
        
        # Analytic
        self.is_green = self.data.close > self.data.open
        self.is_red = not self.is_green
        self.direction = 1 if self.is_green else -1
        self.bar_body_low = min ([self.data.close, self.data.open])
        self.bar_body_high = max([self.data.close, self.data.open])
        
        # Volume
        self.volume_ema = 0
        
        self.indicators = {}
        
        # Pattern
        self.micro_pullback_likelihood = 0
        
        # Signals
        self.entry_signal = np.nan
        self.exit_signal = np.nan
        self.reason = None

class KlineBarGroup:
    
    def __init__(self, bar: KlineBar = None) -> None:
        self.count = 0
        if bar is None:
            return
        self._add_first_bar(bar)
        
    def _add_first_bar(self, bar: KlineBar):
        self.direction = 1 if bar.is_green else -1
        self.directions = [bar.direction]
        self.is_up = self.direction == 1
        self.is_down = self.direction == -1
        
        self.start_index = bar.index
        self.end_index = bar.index
        self.count = 1
        
        self.volume = bar.data.volume
        self.high = bar.data.high
        self.low = bar.data.low
        self.body_high = bar.bar_body_high
        self.body_low = bar.bar_body_low
        self.range = self.body_high - self.body_low
        
        self.tick_max_volume = bar.data.volume
        
        self.open = bar.data.open
        self.close = bar.data.close
        
    def add_bar(self, bar: KlineBar):
        if self.count == 0:
            self._add_first_bar(bar)
            return
        if bar.direction != 0 and bar.direction != self.direction:
            bar.direction = 0
            self.is_up = False
            self.is_down = False
        self.directions.append(bar.direction)
        self.count += 1
        self.volume += bar.data.volume
        self.end_index = bar.index
        self.high = max(self.high, bar.data.high)
        self.low = min(self.low, bar.data.low)
        self.body_high = max(self.body_high, bar.bar_body_high)
        self.body_low = min(self.body_low, bar.bar_body_low)
        self.tick_max_volume = max(self.tick_max_volume, bar.data.volume)
        self.range = self.body_high - self.body_low
        self.close = bar.data.close
        
    def get_candles(self, kline: list[KlineBar]):
        return kline[self.start_index:self.end_index+self.count]