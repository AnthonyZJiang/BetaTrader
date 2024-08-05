from betatrader.trendanalyser.common.kline import KlineBar, KlineBarGroup

class BullFlag:
    def __init__(self, pole_trend: KlineBarGroup) -> None:
        if pole_trend.is_down:
            self.valid = False
            return
        self.valid = True
        self.pole_trend = pole_trend
        self.flag: KlineBarGroup = None
    
    def analyse(self, flag: KlineBarGroup):
        if not self.valid:
            return 0
        
        if flag.count < 3:
            return 0
        
        if flag.tick_max_volume > self.pole_trend.tick_max_volume:
            return 0
        if flag.body_high > self.pole_trend.body_high:
            return 0
        if flag.range > self.pole_trend.range * 0.3:
            return 0
        return 1