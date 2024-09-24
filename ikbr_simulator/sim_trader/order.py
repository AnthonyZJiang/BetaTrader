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
    def __init__(self, portfolio, symbol:str | None, action:OrderAction, quantity:int, limit:float=None, stop:float=None):
        if symbol is None:
            # return an empty order for user to fill in.
            return
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

        self.date_time_last_update = self.date_time
        self.value = 0.0
        self.avg_price = 0.0
        self.fee = 0.0
        self.filled = 0
        self.unfilled = quantity
        self.status = OrderStatus.OPEN
        
        self.portfolio = portfolio
    
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
        self.date_time_last_update = datetime.datetime.now()
        self.portfolio.update_cash(price * quantity * (-1 if self.action == OrderAction.BUY else 1) - self.fee)
        return quantity
    
    def cancel(self):
        if self.filled > 0:
            self.status = OrderStatus.PARTIAL
            self.fee = max(0.0035*self.filled, 0.35)
        else:
            self.status = OrderStatus.CANCELLED
        self.date_time_last_update = datetime.datetime.now()
        self.portfolio.update_cash(-self.fee)
        return self.quantity - self.filled
    
    def __str__(self):
        return "Order#%-3d %-4s %s %-6s | %s | LMT: %3.2f STP: %3.2f FILLED: %4d/%4d | AVG_PRC: %5.2f | FEE: %5.2f" % (
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
        return "%s,%s,%d,%s,%s,%s,%s,%.2f,%.2f,%d,%d,%.2f,%.2f" % (
            self.date_time.strftime("%Y-%m-%d %H:%M:%S"),
            self.date_time_last_update.strftime("%Y-%m-%d %H:%M:%S"),
            self.id, 
            self.symbol, 
            self.action, 
            self.order_type,
            self.status,
            self.limit if self.limit is not None else 0.0, 
            self.stop if self.stop is not None else 0.0,
            self.quantity,
            self.filled,
            self.avg_price,
            self.fee)
        
    def _from_csv(self, csv: str):
        items = csv.split(",")
        if len(items) != 13:
            raise ValueError("Invalid number of items in CSV")
        self.date_time = datetime.datetime.strptime(items[0], "%Y-%m-%d %H:%M:%S")
        self.date_time_last_update = datetime.datetime.strptime(items[1], "%Y-%m-%d %H:%M:%S")
        self.id = int(items[2])
        self.symbol = items[3]
        self.action = OrderAction(items[4])
        self.order_type = OrderType(items[5])
        self.status = OrderStatus(items[6])
        self.limit = float(items[7])
        self.stop = float(items[8])
        self.quantity = int(items[9])
        self.filled = int(items[10])
        self.avg_price = float(items[11])
        self.fee = float(items[12])
        self.unfilled = self.quantity - self.filled
        self.value = self.avg_price * self.filled
        
    @staticmethod
    def from_csv(csv: str):
        order = Order(None, None, None, None)
        order._from_csv(csv)
        return order