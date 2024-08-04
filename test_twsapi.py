from threading import Thread
from datetime import datetime
from ibapi.client import *
from ibapi.wrapper import *
from twsapp.historicaldata import HistoricalDataStore
from twsapp.twsapp import TWSApp


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
        

class ScannerVisualizer:
    rank_list_size = 50
    
    def __init__(self, tws: TWSApp):
        self.tws = tws
        self.rank_list: list[RankListDataStore] = [None] * self.rank_list_size
        self.rank_max = 0
        
    def run(self):
        
        while True:
            if not self.tws.scanner_data_ready:
                continue
            rank_n = len(self.tws.histdata_req_id_lookup) / 2
            if rank_n == 0:
                continue
            rank_max = min(rank_n, self.rank_list_size)
            
            rank_list_refreshed = self.populate_rank_list()
            if not rank_list_refreshed:
                continue
            print("-"*50)
            c = 0
            for rank in range(rank_max):
                if self.rank_list[rank] is None:
                    continue
                r = self.rank_list[rank]
                if r.price_perc_change < 0.1:
                    continue
                c += 1
                print(f"#{c}: {r.symbol}, Close: {r.today_day_bar.close}, DiffCH: {r.close_high_diff}, Vol.: {r.today_day_bar.volume}, Rel.Vol.: {r.relative_vol*100:0.2f}, Price Percent Change: {r.price_perc_change*100:0.2f}")
    
    def populate_rank_list(self):
        rank_list_refreshed = False
        while True:
            try:
                histdata = self.tws.received_histdata.get_nowait()
            except queue.Empty:
                break
            
            if histdata.req_id not in self.tws.histdata_req_id_lookup:
                continue
            rank = self.tws.histdata_req_id_lookup[histdata.req_id]
            if rank >= self.rank_list_size:
                continue
            
            if self.rank_list[rank] is None or self.rank_list[rank].symbol != histdata.symbol:
                # if current entry at rank is empty or symbol is different
                self.rank_list[rank] = RankListDataStore(histdata.symbol, rank)
            
            if histdata.duration == "2 D":
                if ScannerVisualizer.is_today(histdata.bar.date):
                    self.rank_list[rank].set_today_day_bar(histdata)
                else:
                    self.rank_list[rank].set_yesterday_day_bar(histdata)
            elif histdata.interval == "1 min":
                self.rank_list[rank].add_today_min_bar(histdata)
            rank_list_refreshed = True
        return rank_list_refreshed
    
    def is_historical_data_valid(self, hdata):
        return len(hdata) >= 2 and hdata[0] is not None and hdata[1] is not None
    

    @staticmethod
    def to_datetime(date_str: str) -> datetime:
        return datetime.strptime(date_str, "%Y%m%d")
    
    @staticmethod
    def is_today(self, date_str: str) -> bool:
        return ScannerVisualizer.to_datetime(date_str).date() == datetime.now().date()

def main():
    app = TWSApp() 
    app.connect("127.0.0.1", 7496, clientId=0)
    tws_trader = Thread(target=app.run)
    tws_trader.start()
    viz = ScannerVisualizer(app)
    viz.run()
    

if __name__ == "__main__":
    main()