from datetime import datetime
from ibapi.client import *
from ibapi.wrapper import *

from .twsapp.twsapp import TWSApp
from .ranklist import RankListDataStore


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
            rank_n = int(len(self.tws.histdata_req_id_lookup) / 2)
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
    def is_today(date_str: str) -> bool:
        return ScannerVisualizer.to_datetime(date_str).date() == datetime.now().date()
