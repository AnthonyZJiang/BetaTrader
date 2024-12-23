import logging
import json

from ikbr_simulator.util.twslogging import setup_logger
from ikbr_simulator.sim_trader.portfolio import Portfolio
from ikbr_simulator.tws_app.datastore.fundamentals import StockFundamentals

DEF_TICK_REQ_ID = 2000
DEF_CONTRACT_DETAIL_REQ_ID = 19000
DEF_SUB_GROUP_ID = -1

class TWSCommon:
    
    def __init__(self):
        self.trade_logger = setup_logger('trade', None, logging.INFO, 'trade.log.csv')
        self.logger = setup_logger('sim_twsapp', logging.INFO, logging.DEBUG, 'sim.log')
        
        self.exit_flag = False
        self.is_ready = False
        self.tick_req_id: int = DEF_TICK_REQ_ID
        self.mrk_data_req_id: int = 0
        self.tick_req_id_symbol_map: dict[int, str] = {}
        self.fundamentals: dict[str, StockFundamentals] = {}
        
        self.contract_detail_req_id: int = DEF_CONTRACT_DETAIL_REQ_ID
        self.subscribed_group_id: int = DEF_SUB_GROUP_ID
        self.req_id_callback_map: dict[int, callable] = {}
        
        self.current_symbol = None
        self.current_bid = 0
        self.current_ask = 0
        
        self.gui_update_callback_tracked_symbol = None
        
        self.portfolios: dict[str, Portfolio] = {}
        with open('portfolio.json', 'r') as f:
            portfolio_json = json.load(f)
            for p in portfolio_json:
                name = p['name']
                cash = p['cash']
                self.portfolios[name] = Portfolio(name)
                self.portfolios[name].cash = cash
        self.portfolio = self.portfolios['realistic']
