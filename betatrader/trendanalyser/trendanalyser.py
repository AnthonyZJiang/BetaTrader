from betatrader.trendanalyser.common.maths import *
from .common.kline import KlineBar, KlineBarGroup
from .indicators.macdanalyser import MACDAnalyser
from .indicators.emaanalyser import EMAAnalyser
from .patterns.klinepattern import KlinePatternAnalyser, KlinePatternType as ptype

PERIOD_MACD_FAST = 12
PERIOD_MACD_SLOW = 26
PERIOD_MACD_SIGNAL = 9
PERIOD_EMA_FAST = 9
PERIOD_EMA_SLOW = 20

THRESHOLD_VOLUME = 50000
THRESHOLD_REL_PRICE = 0.1
THRESHOLD_REL_VOLUME = 4


class TrendAnalyser:
    
    def __init__(self):
        self.kline: list[KlineBar] = []
        self.kline_group = KlineBarGroup()
        self.pointer = -1
        self.is_ema9_20_gold_crossed = False
        self.is_ema9_20_death_crossed = True
        self.is_macd_gold_crossed = False
        self.is_macd_death_crossed = True
        self.macd_analyser = MACDAnalyser(PERIOD_MACD_FAST, PERIOD_MACD_SLOW, PERIOD_MACD_SIGNAL)
        self.ema_analyser = EMAAnalyser(PERIOD_EMA_FAST, PERIOD_EMA_SLOW)
        self.pattern_analyser = KlinePatternAnalyser()
        self.this_tick = None
        self.prev_tick = None
        self._hot = False
        
    def add_bar(self, tick_packet):
        self.pointer += 1
        self.this_tick = KlineBar(tick_packet, self.pointer)
        
        # assume this bar follows the previous trend.
        if self.pointer > 0:
            self.prev_tick = self.kline[self.pointer-1]
            self.this_tick.ema_good = self.prev_tick.ema_good
            self.this_tick.macd_good = self.prev_tick.macd_good
        
        
        self.kline.append(self.this_tick)
        self.kline_group.add_bar(self.this_tick)
        
        # calculate tech indicators
        self.macd_analyser.calculate(self.kline)
        self.ema_analyser.calculate(self.kline)
        
        # At least 4 data points required for the rest 
        if self.pointer < 4:
            return
        if not self._is_hot():
            return
        self.pattern_analyser.add_bar(self.this_tick)
        self._analyse_signal()
        
    def _is_hot(self):
        if self._hot:
            return True
        if self.this_tick.volume < THRESHOLD_VOLUME:
            return False
        if (self.this_tick.volume - self.prev_tick.volume) / self.prev_tick.volume < THRESHOLD_REL_VOLUME:
            return False
        if (self.this_tick.close_price - self.prev_tick.close_price) / self.prev_tick.close_price < THRESHOLD_REL_PRICE:
            return False
        self._hot = True
        return True
        
    def _analyse_signal(self):
        # micro pullback entry signal
        # prev
        # this_pattern = self.pattern_analyser.get_pattern_by_index(self.pointer)
        # if self.this_tick.is_green:
            
        #     if self.prev_tick.micro_pullback_likelihood > 0.5 or self.kline[self.pointer-2].micro_pullback_likelihood > 0.5:
        #         self.this_tick.entry_signal = self.this_tick.open_price
        #         self.this_tick.reason = "mpb"
        #     previous_high = max([i.open_price for i in self.kline[self.pointer-1:self.prev_tick.trend_length+1:-1]])
        #     if self.this_tick.high_price > previous_high:
        #         self.this_tick.entry_signal = previous_high
        #         self.this_tick.reason = "mpb"
        #         return
            
        # ema death cross
        if self.this_tick.ema_death_cross:
            self.this_tick.exit_signal = self.this_tick.close_price
            self.this_tick.reason = "deathcross"
            return
        
        # ema gold cross while ema and macd are good
        if self.this_tick.ema_golden_cross and self.this_tick.ema_good and self.this_tick.macd_good:
            # TODO check for making a new high!
            self.this_tick.entry_signal = self.this_tick.bar.open
            self.this_tick.reason = "goldencross"
            return