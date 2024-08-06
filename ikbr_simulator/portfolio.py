from rich.table import Table
from rich.console import Console

from .order import Order, OrderAction, OrderStatus, OrderType


class Portfolio:
    def __init__(self):
        self.orders: dict[str, list[Order]] = {} # symbol: [Order]
        
    def add_order(self, order: Order):
        if not order.symbol in self.orders:
            self.orders[order.symbol] = [order]
        elif not order in self.orders[order.symbol]:
            self.orders[order.symbol].append(order)
    
    def get_all_positions(self) -> dict[str, list[int]]:
        positions = {
            '_cash_': [0, 1]
        }
        for symbol in self.orders:
            positions[symbol] = [0, 0]
            for order in self.orders[symbol]:
                if order.action == OrderAction.BUY:
                    positions[symbol][0] += order.filled
                    positions[symbol][1] += order.value
                    positions["_cash_"][0] -= order.value + order.fee
                elif order.action == OrderAction.SELL:
                    positions[symbol][0] -= order.filled
                    positions[symbol][1] -= order.avg_price * order.filled
                    positions["_cash_"][0] += order.value - order.fee
            if positions[symbol][0] != 0:
                positions[symbol][1] /= positions[symbol][0]
        return positions
    
    def get_position(self, symbol: str) -> list[int]:
        positions = self.get_all_positions()
        if not symbol in positions:
            return [0, 0]
        return positions[symbol]
        
    def print_positions(self):
        positions = self.get_all_positions()
        table = Table(title="Portfolio")
        table.add_column("Symbol")
        table.add_column("Quantity")
        table.add_column("Avg Price")
        table.add_column("Value")
        total_value = 0
        for symbol, (quantity, avg_price) in positions.items():
            if symbol == "_cash_":
                symbol = "CASH"
                quantity_s = ''
                avg_price_s = ''
            elif quantity == 0:
                continue
            else:
                quantity_s = str(quantity)
                avg_price_s = "%.2f" % avg_price
            value = quantity * avg_price
            if value < 0:
                value_s = "[red]%.2f" % value
            else:
                value_s = "[green]%.2f" % value
            table.add_row(symbol.upper(), quantity_s, avg_price_s, value_s)
            total_value += value
        if total_value < 0:
            colour = "red"
        else:
            colour = "green"
        table.add_row(f"[{colour}]TOTAL", "", "", f"[{colour}]{total_value:.2f}")
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
        table.add_column("Avg price")
        table.add_column("Limit")
        table.add_column("Status")
        table.add_column("Value")
        for orders in self.orders.values():
            for order in orders:
                table.add_row(str(order.id), 
                              order.symbol, 
                              order.date_time.strftime("%H:%M:%S"), 
                              "[green]BUY" if order.action == OrderAction.BUY else "[red]SELL", 
                              "MKT" if order.order_type == OrderType.MARKET else "LMT" if order.order_type == OrderType.LIMIT else "STP" if order.order_type == OrderType.STOP else "STP_LMT",
                              f"{order.filled}/{order.quantity}",
                              "N/A" if order.stop is None else "%.2f" % order.stop,
                              str(order.avg_price), 
                              "N/A" if order.limit is None else "%.2f" % order.limit, 
                              "[green]FILLED" if order.status == OrderStatus.FILLED else "[red]CANCELLED" if order.status == OrderStatus.CANCELLED else "[yellow]OPEN" if order.status == OrderStatus.OPEN else "[purple]PARTIAL",
                              "%.2f" % order.value)
            table.add_section()
        console = Console()
        console.print(table)