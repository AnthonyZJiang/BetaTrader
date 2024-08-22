from rich.console import Console
from rich.table import Table
from threading import Thread
import logging

from .tws_app import TWSApp
from .util.logging import setup_logger
from .sim_trader.order import Order, OrderAction, OrderStatus


DEFAULT_ORDER_SIZE = 100

class SimulatorCLI:
    
    def __init__(self):
        self.logger = setup_logger('sim_cli', None, logging.DEBUG, 'sim.log')
        self.tws_app = None
        self.app_thread = None
        self.order = None
        self.default_quantity = DEFAULT_ORDER_SIZE
        self.quantity_multiplier = 100
        
    def run(self):
        self.tws_app = TWSApp()
        self.tws_app.tws_common.gui_update_callback_tracked_symbol = self._gui_update_callback_tracked_symbol
        self.tws_app.connect("127.0.0.1", 7496, clientId=1)
        self.app_thread = Thread(target=self.tws_app.run)
        self.app_thread.start()
        while not self.tws_app.tws_common.is_ready:
            pass
        self.tws_app.link_display_group(1)
        exit_flag = False
        self.print_tracking_symbol = False
        while not exit_flag:
            try:
                exit_flag = not self._take_command()
            except ValueError as e:
                print("Invalid argument")
                self.logger.error(e)
            except Exception as e:
                print("An unknown error occurred, check log for details.")
                self.logger.error(e, exc_info=True)
        self.tws_app.disconnect()
        self.app_thread.join()
        
    def _gui_update_callback_tracked_symbol(self, symbol):
        print(f"Tracking symbol: {symbol}")

    def _place_order(self, order: Order):
        if order.symbol is None:
            return
        self.tws_app.place_order(order)

    def _take_command(self):
        if self.print_tracking_symbol:
            print("Tracking symbol:", self.tws_app.tws_common.current_symbol)
        self.print_tracking_symbol = True
        val = input("")
        if val == "exit":
            ans = input("Do you want to export the trades? (y/n)")
            if ans == "y":
                ans = input("Enter the file name: (default: trades.csv)")
                if ans == "":
                    ans = "trades.csv"
                self.tws_app.tws_common.portfolio.export_trades(ans)
                print("Trades exported to ", ans)
            print("Exiting")
            self.tws_app.disconnect()
            return False
        return self._process_command(val.lower().split())
        
    def _process_command(self, args: dict[str]):
        nargs = len(args)

        match args[0]:
            case "help":
                self._print_help()
            case "set":
                self._set_parameters(*args[1:])
            case "ls":
                if nargs == 1:
                    self.tws_app.tws_common.portfolio.print_all_trades()
                elif args[1] == "pos":
                    self.tws_app.tws_common.portfolio.print_positions()
            case "track":
                self._set_track(*args[1:])
            case "t":
                self._set_track(*args[1:])
            case "link":
                if nargs == 1:
                    print("No value provided")
                    return True
                self.print_tracking_symbol = False
                id = int(args[1])
                self.tws_app.link_display_group(id)
            case "b":
                order = self._get_order(OrderAction.BUY, *args[1:])
                self._place_order(order)
            case "s":
                order = self._get_order(OrderAction.SELL, *args[1:])
                self._place_order(order)
            case "cl":
                pos = self.tws_app.tws_common.portfolio.get_position(self.tws_app.tws_common.current_symbol)
                if pos is None or pos.quantity <= 0:
                    print("No position to close")
                    return True
                order = Order(self.tws_app.tws_common.current_symbol, OrderAction.SELL, pos.quantity)
                self._place_order(order)
            case "c":
                if nargs == 1:
                    print("No value provided")
                    return True
                order_id = int(args[1])
                self.tws_app.cancel_order(order_id)
            case "export":
                if nargs == 1:
                    dest = "trades.csv"
                else:
                    dest = args[1]
                self.tws_app.tws_common.portfolio.export_trades(dest)
            case _:
                if args[0].startswith("s") or args[0].startswith("b"):
                    return self._process_command([args[0][0], args[0][1:]] + args[1:])
                else:
                    print("Invalid command")
        return True
        
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
    
    def _set_track(self, *args):
        if len(args) == 0:
            print("No value provided")
            return
        symbol = args[0].upper()
        self.tws_app.update_linked_group_by_symbol(symbol)

    def _get_order(self, action: OrderAction, *args):
        quantity = self.default_quantity
        limit = None
        stop = None
        i = 0
        while i < len(args):
            if args[i] == "l":
                limit = float(args[i+1])
                i += 2
            elif args[i] == "st":
                stop = float(args[i+1])
                i += 2
            elif args
            elif args[i].startswith("l"):
                limit = int(args[i][1:])
                i += 1
            elif args[i].startswith("st"):
                stop = float(args[i][2:])
                i += 1
            elif i == 0:
                quantity = float(args[i])*self.quantity_multiplier
                i += 1
            elif i == 1:
                limit = float(args[i])
                i += 1
            else:
                i += 1
        return Order(self.tws_app.tws_common.current_symbol, action, quantity, limit, stop)

    def _set_parameters(self, *args):
        nargs = len(args)
        if nargs == 0:
            return
        match args[0]:
            case "default_quantity":
                if nargs == 1:
                    print("No value provided")
                    return
                self.default_quantity = int(args[1])
                print("Default quantity set to", self.default_quantity)
            case "allow_short":
                if nargs == 1:
                    print("No value provided")
                    return
                self.allow_short = True if args[1] == "1" else False
                print("Short selling is", "enabled" if self.allow_short else "disabled")
            case "quantity_multiplier":
                if nargs == 1:
                    print("No value provided")
                    return
                self.quantity_multiplier = int(args[1])
                print("Quantity multiplier set to", self.quantity_multiplier)
            case _:
                print("Unknown parameter")
        self.default_quantity = int(args[1])

    def _print_help(self):
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
