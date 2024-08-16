from rich.console import Console
from rich.table import Table
from threading import Thread
import logging

from .twsapp import TWSApp
from .logging import setup_logger
from .order import Order, OrderAction, OrderStatus


DEFAULT_ORDER_SIZE = 100

class SimulatorCLI:
    
    def __init__(self):
        self.logger = setup_logger('sim_cli', None, logging.DEBUG, 'sim.log')
        self.tws_app = None
        self.app_thread = None
        self.current_symbol = None
        self.order = None
        self.default_quantity = DEFAULT_ORDER_SIZE
        self.quantity_multiplier = 100
        
    def run(self):
        self.tws_app = TWSApp()
        self.tws_app.connect("127.0.0.1", 7496, clientId=1)
        self.app_thread = Thread(target=self.tws_app.run)
        self.app_thread.start()
        exit_flag = False
        while not exit_flag:
            try:
                exit_flag = not self._process_command()
            except Exception as e:
                print("Invalid argument")
                self.logger.error(e)
        self.tws_app.disconnect()
        self.app_thread.join()
        
    def _print_all_orders(self):
        table = Table(title="Orders")
        table.add_column("Order ID")
        table.add_column("Symbol")
        table.add_column("Action")
        table.add_column("Quantity")
        table.add_column("Limit")
        table.add_column("Status")
        for orders in self.tws_app.received_orders.values():
            for order in orders:
                if order.status == OrderStatus.FILLED:
                    status = "[green]FILLED"
                elif order.status == OrderStatus.CANCELLED:
                    status = "[red]CANCELLED"
                else:
                    status = "[yellow]OPEN"
                if order.action == OrderAction.BUY:
                    action = "[green]BUY"
                else:
                    action = "[red]SELL"
                table.add_row(order.id, order.symbol, action, order.quantity, order.limit, status)
        console = Console()
        console.print(table)
    
    def _process_command(self):
        print("Tracking symbol:", self.current_symbol)
        val = input("")
        if val == "exit":
            ans = input("Do you want to export the trades? (y/n)")
            if ans == "y":
                ans = input("Enter the file name: (default: trades.csv)")
                if ans == "":
                    ans = "trades.csv"
                self.tws_app.portfolio.export_trades(ans)
                print("Trades exported to ", ans)
            print("Exiting")
            self.tws_app.disconnect()
            return False
        
        args = val.split()
        narg = len(args)
        quantity = self.default_quantity
        limit = None
        stop = None
        if args[0] == "help":
            console = Console()
            console.rule("Commands")
            console.print("ls [green]Print all orders")
            console.print("ls pos [green]Print all orders or positions")
            console.print("set <default_quantity <quantity>> [green]Set the default quantity, default is 100")
            console.print("set <allow_short <1|0>> [green]Set 1 to allow short selling")
            console.print("track <symbol> [green]Track a symbol")
            console.print("b <q<quantity>> <l<limit>> [green]Buy the tracked symbol")
            console.print("s <q<quantity>> <l<limit>> [green]Sell the tracked symbol")
            console.print("st <q<quantity>> <l<limit>> [green]Set stop loss for the tracked symbol")
            console.print("cl [green]Close the current position for the tracked symbol")
            console.print("c <order_id> [green]Cancel an order")
            console.print("exit [green]Exit the program")
            return True
        if args[0] == "ls":
            if narg == 1:
                self.tws_app.portfolio.print_all_trades()
            elif args[1] == "pos":
                self.tws_app.portfolio.print_positions()
            return True
                      
        if args[0] == "set":
            if narg == 1:
                return True
            if args[1] == "default_quantity":
                if narg == 2:
                    print("No value provided")
                    return True
                self.default_quantity = int(args[2])
            elif args[1] == "allow_short":
                if narg == 2:
                    print("No value provided")
                    return True
                self.allow_short = True if args[2] == "1" else False
            elif args[1] == "quantity_multiplier":
                if narg == 2:
                    print("No value provided")
                    return True
                self.quantity_multiplier = int(args[2])
            self.default_quantity = int(args[1])
            return True
            
        if args[0] == "track":
            if narg == 1:
                print("No value provided")
                return True
            symbol = args[1].upper()
            self.current_symbol = symbol
            self.tws_app.track_symbol(symbol)

        elif args[0] == "b":
            for arg in args[1:]:
                if arg.startswith("q"):
                    quantity = int(arg[1:])*self.quantity_multiplier
                elif arg.startswith("st"):
                    stop = float(arg[2:])
                else:
                    limit = float(arg)
            order = Order(self.current_symbol, OrderAction.BUY, quantity, limit, stop)
            self._place_order(order)
        
        elif args[0] == "s":
            for arg in args[1:]:
                if arg.startswith("q"):
                    quantity = int(arg[1:])*self.quantity_multiplier
                elif arg.startswith("st"):
                    stop = float(arg[2:])
                else:
                    limit = float(arg)
            order = Order(self.current_symbol, OrderAction.SELL, quantity, limit, stop)
            self._place_order(order)
            
        elif args[0] == "close":
            pos = self.tws_app.portfolio.get_position(self.current_symbol)
            if pos is None or pos.quantity <= 0:
                print("No position to close")
                return True
            order = Order(self.current_symbol, OrderAction.SELL, pos.quantity)
            self._place_order(order)
            
        elif args[0] == "c":
            if narg == 1:
                print("No value provided")
                return True
            order_id = int(args[1])
            self.tws_app.cancel_order(order_id)
            
        elif args[0] == "export":
            if narg == 1:
                dest = "trades.csv"
            else:
                dest = args[1]
            self.tws_app.portfolio.export_trades(dest)
            
        else:
            print("Invalid command")
        return True


    def _place_order(self, order: Order):
        if order.symbol is None:
            return
        self.tws_app.place_order(order)