import math
import numpy as np
from .maths import *

class KlineTick:
    
    def __init__(self, data):
        self.data = data
        self.open_price = data['open']
        self.close_price = data['close']
        self.high_price = data['high']
        self.low_price = data['low']
        self.volume = data['volume']
        self.is_green = self.close_price > self.open_price
        self.is_red = not self.is_green
        self.in_up_trend = False
        self.trend_since = 0
        self.trend_length = 0
        self.micro_pullback_likelihood = 0
        self.ema9 = 0
        self.ema20 = 0
        self.ema12 = 0
        self.ema26 = 0
        self.macd = 0
        self.macd_signal = 0
        self.macd_curve = 0
        self.entry_signal = np.nan
        self.exit_signal = np.nan
    

class TrendAnalyser:
    
    def __init__(self):
        self.klines: list[KlineTick] = []
        self.pointer = -1
        self.is_ema9_20_gold_crossed = False
        self.is_ema9_20_death_crossed = True
        self.is_macd_gold_crossed = False
        self.is_macd_death_crossed = True
        
    def add_tick(self, tick):
        self.klines.append(KlineTick(tick))
        self.pointer += 1
        if self.pointer == 0:
            return
        if self.klines[self.pointer].is_green and self.klines[self.pointer-1].is_green:
            self.klines[self.pointer].in_up_trend = True
            self.klines[self.pointer].trend_since = self.klines[self.pointer-1].trend_since
        elif self.klines[self.pointer].is_red and self.klines[self.pointer-1].is_red:
            self.klines[self.pointer].in_up_trend = False
            self.klines[self.pointer].trend_since = self.klines[self.pointer-1].trend_since
        else:
            self.klines[self.pointer].in_up_trend = self.klines[self.pointer].is_green
            self.klines[self.pointer].trend_since = self.pointer
        self.klines[self.pointer].trend_length = self.pointer - self.klines[self.pointer].trend_since + 1
        
        self.check_signals()
        
    
    def calculate_micro_pullback_pattern(self) -> float:
        """Returns likelihood of a micro pullback pattern"""
        if self.klines[self.pointer].is_green:
            return 0
        if self.pointer < 4:
            return 0
        likelihood = 1
        
        down_trend_length = self.klines[self.pointer].trend_length
        likelihood -= 0.3 * (down_trend_length - 1)
        if likelihood < 0:
            return 0
        print(self.klines[-1].data['date'])
        down_trend_start = self.klines[self.pointer].trend_since
        up_trend_end = self.pointer - down_trend_length
        up_trend_start = self.klines[up_trend_end].trend_since
        
        red_candles = self.klines[down_trend_start:self.pointer + 1]
        red_max_volume = max([c.volume for c in red_candles])
        red_min_close = min([c.close_price for c in red_candles])
        green_candles = self.klines[up_trend_start:up_trend_end + 1]
        green_max_volume = max([c.volume for c in green_candles])
        green_max_open = max([c.open_price for c in green_candles])
        green_last_close = self.klines[up_trend_end].close_price
        up_amount = self.klines[up_trend_end].close_price - green_candles[0].open_price
        drop_amount = green_last_close - red_min_close
        
        if green_max_volume == 0:
            return 0
        
        if red_min_close < green_max_open or drop_amount/up_amount > 0.3:
            return 0
        
        ratio = red_max_volume/green_max_volume
        deduction = -0.01 - 0.003 * math.exp(5.87*ratio)
        deduction = max(0, deduction)
        likelihood += deduction
        self.klines[self.pointer].micro_pullback_likelihood = likelihood
        
    def calculate_macd(self):
        self.klines[self.pointer].macd_curve = self.klines[self.pointer].ema12 - self.klines[self.pointer].ema26
        self.klines[self.pointer].macd_signal = ema(self.klines[self.pointer].macd_curve, self.klines[self.pointer-1].macd_signal, 9)
        self.klines[self.pointer].macd = self.klines[self.pointer].macd_curve - self.klines[self.pointer].macd_signal
        
    def calculate_ema(self):
        if self.pointer == 0:
            return
        close_price = self.klines[self.pointer].close_price
        self.klines[self.pointer].ema9 = ema(close_price, self.klines[self.pointer-1].ema9, 9)
        self.klines[self.pointer].ema12 = ema(close_price, self.klines[self.pointer-1].ema12, 12)
        self.klines[self.pointer].ema20 = ema(close_price, self.klines[self.pointer-1].ema20, 20)
        self.klines[self.pointer].ema26 = ema(close_price, self.klines[self.pointer-1].ema26, 26)
    
    def check_signals(self):
        self.calculate_micro_pullback_pattern()
        self.calculate_ema()
        self.calculate_macd()
        
        if self.klines[self.pointer - 1].micro_pullback_likelihood and self.klines[self.pointer].is_green > 0.5:
            previous_high = max([i.open_price for i in self.klines[self.pointer-1:self.klines[self.pointer - 1].trend_length+1:-1]])
            if self.klines[self.pointer].high_price > previous_high:
                self.klines[self.pointer].entry_signal = previous_high
            return
        
        gold_crossed = False
        death_crossed = False
        
        if self.klines[self.pointer].ema9 >= self.klines[self.pointer].ema20:
            ema_good = True
            if self.is_ema9_20_death_crossed:
                self.is_ema9_20_gold_crossed = True
                self.is_ema9_20_death_crossed = False
                gold_crossed = True
        else:
            ema_good = False
            if self.is_ema9_20_gold_crossed:
                self.is_ema9_20_death_crossed = True
                self.is_ema9_20_gold_crossed = False
                death_crossed = True

        if self.klines[self.pointer].macd >= 0:
            if self.is_macd_death_crossed:
                self.is_macd_gold_crossed = True
                self.is_macd_death_crossed = False
                gold_crossed = True
            if self.klines[self.pointer].macd_curve > 0:
                macd_good = True
            else:
                macd_good = False
        else:
            macd_good = False
            if self.is_macd_gold_crossed:
                self.is_macd_death_crossed = True
                self.is_macd_gold_crossed = False
                death_crossed = True
        
        if gold_crossed and ema_good and macd_good:
            self.klines[self.pointer].entry_signal = self.klines[self.pointer].open_price
        elif death_crossed and not ema_good and not macd_good:
            self.klines[self.pointer].exit_signal = self.klines[self.pointer].close_price
        
        