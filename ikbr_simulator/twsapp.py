from queue import Queue
from decimal import Decimal

from ibapi.client import *
from ibapi.common import ListOfContractDescription, TickAttribBidAsk
from ibapi.wrapper import *

from .logging import setup_logger
from .order import Order, OrderAction, OrderStatus, OrderType
from .portfolio import Portfolio


class TWSApp(EWrapper, EClient):
    
    def __init__(self):
        EClient.__init__(self, self)
        self.trade_logger = setup_logger('trade', None, logging.INFO)
        self.logger = setup_logger('sim_twsapp', logging.INFO, logging.DEBUG, 'sim.log')
        self.portfolio = Portfolio()
        
        self.tracked_symbol = None
        self.tick_by_tick_req_id = 2000
        self.new_orders: Queue[Order] = Queue()
        self.received_orders: dict[str, list[Order]] = {} # symbol: [Order]
        self.req_id_lookup: dict[int, str] = {} # req_id: symbol
        self.order_id_lookup: dict[int, Order] = {} # order_id: Order
        self.is_ready = False
        self.allow_short = False
        
    def nextValidId(self, orderId: int):
        self.is_ready = True
        
    def place_order(self, order: Order):
        self.new_orders.put(order)
        self.order_id_lookup[order.id] = order
        self.track_symbol(order.symbol, False)
        
    def cancel_order(self, order_id: int):
        if order_id in self.order_id_lookup:
            order = self.order_id_lookup[order_id]
            order.cancel()
            self.log_order(order)
            self.order_id_lookup.pop(order_id)
        
    def track_symbol(self, symbol, update_tracked = True):
        if symbol == self.tracked_symbol:
            return
        if update_tracked:
            self.tracked_symbol = symbol
        if symbol in self.req_id_lookup.values():
            return
        if len(self.req_id_lookup) >= 5:
            # can track only 5 symbols at a time
            self.free_up_track_symbol()
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "smart"
        contract.currency = "USD"
        self.reqTickByTickData(self.tick_by_tick_req_id , contract, "BidAsk", 1, False)
        self.req_id_lookup[self.tick_by_tick_req_id] = symbol
        self.tick_by_tick_req_id += 1
        
    def cancel_track_symbol(self, reqId):
        self.cancelTickByTickData(reqId)
        self.req_id_lookup.pop(reqId)
        
    def free_up_track_symbol(self):
        for reqId, symbol in self.req_id_lookup.items():
            if symbol != self.tracked_symbol and not self.any_order(symbol):
                self.cancel_track_symbol(reqId)
                self.logger.warn(f"Max number of symbol tracking reached. Untracking symbol: {symbol}...")
                return
            
    def tickByTickBidAsk(self, reqId: int, time_: int, bidPrice: float, askPrice: float, bidSize: Decimal, askSize: Decimal, tickAttribBidAsk: TickAttribBidAsk):
        try:
            while True:
                order = self.new_orders.get_nowait()
                if order.status != OrderStatus.OPEN:
                    continue
                if order.symbol in self.received_orders:
                    self.received_orders[order.symbol].append(order)
                else:
                    self.received_orders[order.symbol] = [order]
                
                self.portfolio.add_order(order)
                self.logger.info(f"Order received  : {order}")
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.error(f"Error: {e}", exc_info=True)
        if reqId not in self.req_id_lookup:
            return
        sym = self.req_id_lookup[reqId]
        self.portfolio.update_last(sym, askPrice)
        if not self.any_order(sym):
            if sym != self.tracked_symbol:
                if not sym in self.portfolio.entries:
                    self.cancel_track_symbol(reqId)                  
            return
        for order in self.received_orders[sym]:
            if order.status == OrderStatus.CANCELLED or order.status == OrderStatus.PARTIAL:
                continue
            if order.status == OrderStatus.OPEN:
                if order.action == OrderAction.BUY:
                    filled = self.fill_buy_order(order, askPrice, askSize)
                if order.action == OrderAction.SELL:
                    filled = self.fill_sell_order(order, bidPrice, bidSize)
            if filled > 0:
                self.log_order(order)
            if order.status == OrderStatus.FILLED:
                self.received_orders[sym].remove(order)
                
    def any_order(self, symbol):
        return symbol in self.received_orders and len(self.received_orders[symbol]) > 0
                
    def log_order(self, order: Order):
        if order.status == OrderStatus.FILLED:
            self.logger.info(f"Order filled    : {order}")
            self.trade_logger.info(order.to_csv())
        elif order.status == OrderStatus.CANCELLED:
            self.logger.info(f"Order cancelled : {order}")
            self.trade_logger.info(order.to_csv())
        else:
            self.logger.info(f"Order updated   : {order}")
            
    def fill_order(self, order: Order, ask_price, ask_size):
        if order.action == OrderAction.BUY:
            if order.order_type == OrderType.MARKET:
                return order.add_fill(ask_price, int(ask_size*100))
            if order.order_type == OrderType.LIMIT:
                if order.limit >= ask_price:
                   return order.add_fill(ask_price, int(ask_size*100))
                    
    def fill_buy_order(self, order: Order, ask_price, ask_size):
        if order.order_type == OrderType.MARKET:
            return order.add_fill(ask_price, int(ask_size*100))
        elif order.order_type == OrderType.LIMIT:
            if order.limit >= ask_price:
                return order.add_fill(ask_price, int(ask_size*100))
        elif order.order_type == OrderType.STOP:
            if order.stop <= ask_price:
                return order.add_fill(ask_price, int(ask_size*100))
        elif order.order_type == OrderType.STOP_LIMIT:
            if order.stop <= ask_price:
                if order.limit >= ask_price:
                    return order.add_fill(ask_price, int(ask_size*100))
        return 0
    
    def fill_sell_order(self, order: Order, bid_price, bid_size):
        pos = self.portfolio.get_position(order.symbol)
        if pos.quantity <= 0:
            self.logger.info(f"Warning: Short selling not allowed.")
            self.cancel_order(order.id)
            return 0
        max_fill = min(pos.quantity, int(bid_size*100))
        if order.order_type == OrderType.MARKET:
            return order.add_fill(bid_price, max_fill)
        elif order.order_type == OrderType.LIMIT:
            if order.limit <= bid_price:
                return order.add_fill(bid_price, max_fill)
        elif order.order_type == OrderType.STOP:
            if order.stop >= bid_price:
                return order.add_fill(bid_price, max_fill)
        elif order.order_type == OrderType.STOP_LIMIT:
            if order.stop >= bid_price:
                if order.limit <= bid_price:
                    return order.add_fill(bid_price, max_fill)
        return 0

    def error(self, errorCode, reqId, errorString, placeholder=None):
        if errorCode > -1:
            self.logger.error(f"Error code: {errorCode}, {reqId}, {errorString}")
        else:
            self.logger.debug(f"TWSError: {errorCode}, {reqId}, {errorString}")