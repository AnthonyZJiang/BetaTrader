import logging
import json

from ikbr_simulator.util.twslogging import setup_logger
from ikbr_simulator.sim_trader.portfolio import Portfolio
from .datastore.histdatastore import HistDataStore

DEF_TICK_REQ_ID = 2000
DEF_HIST_DATA_REQ_ID = 3000
DEF_SUB_GROUP_ID = -1

class TWSCommon:
    
    def __init__(self):
        self.trade_logger = setup_logger('trade', None, logging.INFO, 'trade.log.csv')
        self.logger = setup_logger('sim_twsapp', logging.INFO, logging.DEBUG, 'sim.log')
        self.portfolio = Portfolio()
        
        self.is_ready = False
        
        self.tick_req_id: int = DEF_TICK_REQ_ID
        self.tick_req_id_symbol_map: dict[int, str] = {}
        
        self.mrk_data_req_id: int = 0
        
        self.hist_data_req_id: int = DEF_HIST_DATA_REQ_ID
        self.hist_data_req_id_symbol_map: dict[int, str] = {}
        self.hist_data: dict[str, HistDataStore] = {}
        
        self.subscribed_group_id: int = DEF_SUB_GROUP_ID
        self.req_id_callback_map: dict[int, callable] = {}
        
        self.current_symbol = None
        self.current_bid = 0
        self.current_ask = 0
        
        self.gui_update_callback_tracked_symbol = None
