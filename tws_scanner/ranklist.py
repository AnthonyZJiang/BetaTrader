from ibapi.client import BarData
from .twsapp.historicaldata import HistoricalDataStore

class RankListDataStore:
    def __init__(self, symbol: str, rank: int):
        self.symbol = symbol
        self.rank = rank
        self.yesterday_day_bar: BarData = None # type: 
        self.today_day_bar: BarData = None # type: 
        self.today_min_bars: list[BarData] = []
        
        self.close_high_diff = 0
        self.relative_vol = 0
        self.price_perc_change = 0
        
    def add_today_min_bar(self, histdata: HistoricalDataStore):
        self.today_min_bars.append(histdata.bar)
        self._cal_min_analytics()
        
    def set_today_day_bar(self, histdata: HistoricalDataStore):
        self.today_day_bar = histdata.bar
        self.close_high_diff = self.today_day_bar.close - self.today_day_bar.high
        self._cal_day_analytics()
        
    def set_yesterday_day_bar(self, histdata: HistoricalDataStore):
        self.yesterday_day_bar = histdata.bar
        self._cal_day_analytics()
        
    def _cal_min_analytics(self):
        pass
        
    def _cal_day_analytics(self):
        self._relative_vol()
        self._price_percent_change()
    
    def _relative_vol(self):
        if self.yesterday_day_bar is None or self.today_day_bar is None:
            return
        if self.yesterday_day_bar.volume == 0:
            self.relative_vol = 999999
        self.relative_vol = self.today_day_bar.volume / self.yesterday_day_bar.volume
    
    def _price_percent_change(self):
        if self.yesterday_day_bar is None or self.today_day_bar is None:
            return
        if self.yesterday_day_bar.close == 0:
            self.relative_vol = 999999
        self.price_perc_change = (self.today_day_bar.close - self.yesterday_day_bar.close) / self.yesterday_day_bar.close
        
    def __str__(self) -> str:
        s = "#%d: %s, Close: %f, DiffCH: %.2f, Vol.: %d, Rel.Vol.: %.1f, Price Percent Change: %.1f" % (
            self.rank, 
            self.symbol, 
            self.today_day_bar.close, 
            self.close_high_diff, 
            self.today_day_bar.volume, 
            self.relative_vol*100, 
            self.price_perc_change*100
            )
        return s