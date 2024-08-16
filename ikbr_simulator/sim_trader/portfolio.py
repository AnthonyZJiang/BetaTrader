from pathlib import Path

from rich.table import Table
from rich.console import Console

from .order import Order, OrderAction, OrderStatus, OrderType


class Position:
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.value = 0
        self.quantity = 0
        self.avg_price = 0
        self.cashflow = 0
        

class PortfolioEntry:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.last = 0
        self.orders: list[Order] = []
        
    def add_order(self, order:Order):
        self.orders.append(order)
        
    def evaluate(self):
        p = Position(self.symbol)
        for order in self.orders:
            if order.action == OrderAction.BUY:
                p.quantity += order.filled
                p.value += order.value
                p.cashflow -= order.fee + order.value
            elif order.action == OrderAction.SELL:
                p.quantity -= order.filled
                p.value -= order.value
                p.cashflow += order.value - order.fee
            if p.quantity > 0:
                p.avg_price = p.value / p.quantity
        return p
    
    @staticmethod
    def from_order(order: Order):
        pe = PortfolioEntry(order.symbol)
        pe.add_order(order)
        pe.last = order.avg_price
        return pe


class Portfolio:
    def __init__(self):
        self.entries: dict[str, PortfolioEntry] = {} # symbol: PortfolioEntry
        
    def update_last(self, symbol: str, last: float):
        if not symbol in self.entries:
            return
        self.entries[symbol].last = last
        
    def add_order(self, order: Order):
        if not order.symbol in self.entries:
            self.entries[order.symbol] = PortfolioEntry.from_order(order)
        elif not order in self.entries[order.symbol].orders:
            self.entries[order.symbol].add_order(order)
    
    def get_all_positions(self) -> dict[str, Position]:
        positions = {
            '_cash_': Position('_cash_')
        }
        for symbol in self.entries:
            positions[symbol] = self.entries[symbol].evaluate()
            positions['_cash_'].value += positions[symbol].cashflow
        return positions
    
    def get_position(self, symbol: str) -> Position | None:
        if not symbol in self.entries:
            return None
        return self.entries[symbol].evaluate()
        
    def print_positions(self):
        positions = self.get_all_positions()
        table = Table(title="Portfolio")
        table.add_column("Symbol")
        table.add_column("Quantity")
        table.add_column("Avg Price")
        table.add_column("Last")
        table.add_column("Change")
        table.add_column("Order Value")
        table.add_column("Last Value")
        table.add_column("Change")
        total_value = 0
        total_change = 0
        
        table.add_row("CASH", "", "", "", "", "",
                    Portfolio.to_green_red_str(positions['_cash_'].value), "")
        table.add_section()
        for symbol, pos in positions.items():
            if symbol == "_cash_":
                continue
            elif pos.quantity == 0:
                continue
            last_value = pos.quantity * self.entries[symbol].last
            value_change = last_value - pos.value
            table.add_row(symbol.upper(),
                          str(pos.quantity), 
                          "%.2f" % pos.avg_price,
                          "%.2f" % self.entries[symbol].last,
                          Portfolio.to_green_red_str(self.entries[symbol].last - pos.avg_price),
                          "%.2f" % pos.value,
                          "%.2f" % last_value, 
                          Portfolio.to_green_red_str(value_change))
            total_value += last_value
            total_change += value_change
        table.add_section()
        table.add_row(f"TOTAL", "", "", "", "", "",
                      Portfolio.to_green_red_str(total_value), 
                      Portfolio.to_green_red_str(total_change))
        console = Console()
        console.print(table)
        
    def print_all_trades(self):
        table = Table(title="Trades")
        table.add_column("ID")
        table.add_column("Symbol")
        table.add_column("Datetime")
        table.add_column("Action")
        table.add_column("Type")
        table.add_column("Quantity")
        table.add_column("Stop price")
        table.add_column("Limit")
        table.add_column("Avg price")
        table.add_column("Value")
        table.add_column("Status")
        for e in self.entries.values():
            for order in e.orders:
                change = e.last - order.avg_price
                table.add_row(str(order.id), 
                              order.symbol, 
                              order.date_time.strftime("%H:%M:%S"), 
                              "[green]BUY" if order.action == OrderAction.BUY else "[red]SELL", 
                              "MKT" if order.order_type == OrderType.MARKET else "LMT" if order.order_type == OrderType.LIMIT else "STP" if order.order_type == OrderType.STOP else "STP_LMT",
                              f"{order.filled}/{order.quantity}",
                              "N/A" if order.limit is None else "%.2f" % order.limit, 
                              "N/A" if order.stop is None else "%.2f" % order.stop,
                              str(order.avg_price),
                              "%.2f" % order.value,"[green]FILLED" if order.status == OrderStatus.FILLED else "[red]CANCELLED" if order.status == OrderStatus.CANCELLED else "[yellow]OPEN" if order.status == OrderStatus.OPEN else "[purple]PARTIAL"
                              )
            table.add_section()
        console = Console()
        console.print(table)
        
    def export_trades(self, destination: str):
        if Path(destination).exists():
            with open(destination, "r") as f:
                first_line = f.readline()
            write_header = first_line == ""
        else:
            write_header = True
        with open(destination, "a") as f:
            if write_header:
                f.write("Date,STK,Time,Action,OrderType,Price,Quantity,Value,Position,Profit,Fee\n")
            for e in self.entries.values():
                current_avg_price = 0
                current_position = 0
                current_value = 0
                for order in e.orders:
                    if order.status == OrderStatus.CANCELLED:
                        continue
                    if order.action == OrderAction.BUY:
                        current_position += order.filled
                        current_value += order.value
                        current_avg_price = current_value/current_position
                        profit = 0
                    else:
                        current_position -= order.filled
                        current_value = current_position * current_avg_price
                        profit = order.avg_price * order.filled - current_avg_price * order.filled
                    f.write("%s,%s,%s,%s,%s,%.3f,%d,%.3f,%d,%.3f,%.3f\n" % (
                            order.date_time.strftime('%Y-%m-%d'),
                            order.symbol,
                            order.date_time.strftime('%H:%M:%S'),
                            order.action,
                            order.order_type,
                            order.avg_price,
                            order.filled,
                            order.value,
                            current_position,
                            profit,
                            order.fee))
        
    @staticmethod
    def to_green_red_str(value):
        if value < 0:
            return f"[red]{value:.2f}"
        return f"[green]{value:.2f}"