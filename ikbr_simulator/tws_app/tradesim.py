import queue
from queue import Queue
from decimal import Decimal

from ibapi.wrapper import *

from ikbr_simulator.sim_trader.order import Order, OrderAction, OrderStatus, OrderType
from .twscommon import TWSCommon
from .tickbidask import TWSTickBidAsk


class TWSTradeSim():
    
    def __init__(self, tws_common: TWSCommon):
        self.tws_common = tws_common
        
        self.new_orders: Queue[Order] = Queue()
        self.received_orders: dict[str, list[Order]] = {} # symbol: [Order]
        self.order_id_lookup: dict[int, Order] = {} # order_id: Order
        self.allow_short = False
        
    def place_order(self, order: Order):
        self.new_orders.put(order)
        self.order_id_lookup[order.id] = order
        TWSTickBidAsk.request_tick_bid_ask(self, order.symbol)
        
    def cancel_order(self, order_id: int):
        if order_id in self.order_id_lookup:
            order = self.order_id_lookup[order_id]
            order.cancel()
            self.log_order(order)
            self.order_id_lookup.pop(order_id)
            
    def process_bid_ask_tick(self, reqId: int, time_: int, bidPrice: float, askPrice: float, bidSize: Decimal, askSize: Decimal, attrib: TickAttribBidAsk):
        try:
            while True:
                order = self.new_orders.get_nowait()
                if order.status != OrderStatus.OPEN:
                    continue
                if order.symbol in self.received_orders:
                    self.received_orders[order.symbol].append(order)
                else:
                    self.received_orders[order.symbol] = [order]
                
                self.tws_common.portfolio.add_order(order)
                self.tws_common.logger.info(f"Order received  : {order}")
        except queue.Empty:
            pass
        except Exception as e:
            self.tws_common.logger.error(f"Error: {e}", exc_info=True)
        if reqId not in self.tws_common.tick_req_id_symbol_map:
            return
        sym = self.tws_common.tick_req_id_symbol_map[reqId]
        self.tws_common.portfolio.update_last(sym, askPrice)
        if not self.any_order(sym):
            if sym != self.tws_common.current_symbol:
                if not sym in self.tws_common.portfolio.entries:
                    TWSTickBidAsk.cancel_tick_bid_ask(self, reqId)                  
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
            self.tws_common.logger.info(f"Order filled    : {order}")
            self.tws_common.trade_logger.info(order.to_csv())
        elif order.status == OrderStatus.CANCELLED:
            self.tws_common.logger.info(f"Order cancelled : {order}")
            self.tws_common.trade_logger.info(order.to_csv())
        else:
            self.tws_common.logger.info(f"Order updated   : {order}")
            
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
        pos = self.tws_common.portfolio.get_position(order.symbol)
        if pos.quantity <= 0:
            self.tws_common.logger.info(f"Warning: Short selling not allowed.")
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
