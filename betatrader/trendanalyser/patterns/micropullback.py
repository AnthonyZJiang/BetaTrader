from betatrader.trendanalyser.kline import KlineTickGroup

class MicroPullback:
    def __init__(self, up_trend: KlineTickGroup) -> None:
        if up_trend.is_down:
            self.valid = False
            return
        self.valid = True
        self.up_trend = up_trend
    
    def analyse(self, sub_group: KlineTickGroup):
        self._validate(sub_group)
        if not self.valid:
            return -1
        return self._is_pattern(sub_group)
        
    def _is_pattern(self, sub_group: KlineTickGroup):
        if sub_group.count > 3:
            return 0
        if sub_group.range/self.up_trend.range > 0.5:
            return 0
        if sub_group.tick_max_volume/self.up_trend.tick_max_volume >= 1:
            return 0
        return 1
    
    def is_pattern_break(self, sub_group: KlineTickGroup):
        if sub_group.count >= 4:
            return True
        elif sub_group.count == 3 and sub_group.directions == [-1, -1, 1]:
            self.valid = True
        elif sub_group.count == 2 and sub_group.directions == [-1, 1]:
            self.valid = True
        else:
            self.valid = False
    