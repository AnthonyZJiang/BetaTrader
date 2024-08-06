from enum import Enum
import datetime


class OrderType(Enum):
    ERROR = 'ERR'
    MARKET = 'MKT'
    LIMIT = 'LMT'
    STOP = 'STP'
    STOP_LIMIT = 'STPLMT'
    
    def __str__(self):
      return self.value
    
    
class OrderAction(Enum):
    BUY = 'B'
    SELL = 'S'
    
    def __str__(self):
      return self.value
    
    
class OrderStatus(Enum):
    OPEN = 'OPEN'
    FILLED = 'FILL'
    CANCELLED = 'CANC'
    PARTIAL = 'PART'
    
    def __str__(self):
      return self.value
    

class Order:
    id = 0
    def __init__(self, symbol:str, action:OrderAction, quantity:int, limit:float=None, stop:float=None):
        self.date_time = datetime.datetime.now()
        self.id = Order.id
        Order.id += 1
        self.symbol = symbol
        self.action = action
        self.quantity = quantity
        self.limit = limit
        self.stop = stop
        self.order_type = OrderType.ERROR
        if self.action == OrderAction.BUY:
            if self.stop is None:
                self.order_type = OrderType.MARKET if self.limit is None else OrderType.LIMIT
            else:
                self.order_type = OrderType.STOP if self.limit is None else OrderType.STOP_LIMIT
        elif self.action == OrderAction.SELL:
            if self.stop is None:
                self.order_type = OrderType.MARKET if self.limit is None else OrderType.LIMIT
            else:
                self.order_type = OrderType.STOP if self.limit is None else OrderType.STOP_LIMIT
        self.value = 0.0
        self.avg_price = 0.0
        self.fee = 0.0
        self.filled = 0
        self.unfilled = quantity
        self.status = OrderStatus.OPEN
    
    def add_fill(self, price: float, quantity: int):
        if self.status != OrderStatus.OPEN:
            return 0
        if quantity > self.unfilled:
            quantity = self.unfilled
        self.value += price * quantity
        self.avg_price = self.value / (self.filled + quantity)
        self.filled += quantity
        self.unfilled -= quantity
        if self.unfilled == 0:
            self.status = OrderStatus.FILLED
            self.fee = max(0.0035*self.filled, 0.35)
        return quantity
    
    def cancel(self):
        if self.filled > 0:
            self.status = OrderStatus.PARTIAL
            self.fee = max(0.0035*self.filled, 0.35)
        else:
            self.status = OrderStatus.CANCELLED
        return self.quantity - self.filled
    
    def __str__(self):
        return "Order#%-3d %-4s %s %-6s | %s | LMT: %3.2f STP: %3.2f FILLED: %4d/%4d | AVG_PRC: %3.2f | FEE: %3.2f" % (
            self.id, 
            self.symbol, 
            self.action, 
            self.order_type,
            self.status,
            self.limit if self.limit is not None else 0.0, 
            self.stop if self.stop is not None else 0.0, 
            self.filled, 
            self.quantity, 
            self.avg_price,
            self.fee)
        
    def to_csv(self):
        return "%s,%d,%s,%s,%s,%s,%.2f,%.2f,%d,%.2f,%.2f" % (
            self.date_time.strftime("%Y-%m-%d %H:%M:%S"),
            self.id, 
            self.symbol, 
            self.action, 
            self.order_type,
            self.status,
            self.limit if self.limit is not None else 0.0, 
            self.stop if self.stop is not None else 0.0,
            self.quantity, 
            self.avg_price,
            self.fee)