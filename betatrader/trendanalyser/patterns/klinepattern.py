from enum import Enum
from betatrader.trendanalyser.common.kline import KlineBar, KlineBarGroup
from .micropullback import MicroPullback
from .bullflag import BullFlag

class KlinePatternType(Enum):
    Invalid = -1
    Unknown = 0
    Micro_pullback = 1
    Bull_flag = 2
    Consolidation = 3
    
class KlinePattern:
    
    def __init__(self, main_group: KlineBarGroup) -> None:
        self.main_group = main_group
        self.sub_group: KlineBarGroup = None
        self.type: KlinePatternType = KlinePatternType.Unknown
        
    def update(self, sub_group: KlineBarGroup, type: KlinePatternType = None):
        self.sub_group = sub_group
        if type is not None:
            self.type = type
            
    def is_in_pattern(self, index: int):
        return self.main_group.start_index <= index <= self.sub_group.end_index
        
    
class KlinePatternAnalyser:
    
    def __init__(self) -> None:
        self.up_trend_group = KlineBarGroup()
        self.sub_group = KlineBarGroup()
        self.up_trend_complete = False
        self.micro_pullback: MicroPullback = None
        self.bull_flag: BullFlag = None
        self.patterns: dict[int, KlinePattern] = {}
        self.patterns_end_indices = {}
    
    def reset(self):
        self.up_trend_group = KlineBarGroup()
        self.sub_group = KlineBarGroup()
        self.up_trend_complete = False
        self.micro_pullback = None
        self.bull_flag = None
    
    def get_pattern_by_index(self, index):
        for pattern in self.patterns.values():
            if pattern.is_in_pattern(index):
                return pattern
    
    def add_bar(self, bar: KlineBar):
        if not self.up_trend_complete:
            if bar.is_green: 
                self.up_trend_group.add_bar(bar)
                return
            if bar.is_red and self.up_trend_group.count == 0:
                return
            else:
                self._complete_up_trend()
        
        self.sub_group.add_bar(bar)    
        self._analyse()
    
    def _complete_up_trend(self):
        self.up_trend_complete = True
        self.micro_pullback = MicroPullback(self.up_trend_group)
        self.bull_flag = BullFlag(self.up_trend_group)
        self.patterns[self.up_trend_group.start_index] = KlinePattern(self.up_trend_group)
    
    def _analyse(self):
        if self.micro_pullback.analyse(self.sub_group) > 0:
            self.patterns[self.up_trend_group.start_index].update(self.sub_group, KlinePatternType.Micro_pullback)
            return
        if self.bull_flag.analyse(self.sub_group) > 0:
            self.patterns[self.up_trend_group.start_index].update(self.sub_group, KlinePatternType.Bull_flag)
            return
        # BUG: existing pattern does not get rejected if they become invalid later on.
        # Unknown pattern, reset and start over
        self.reset()
