from rich.console import Console
from rich.table import Table
from threading import Thread
import logging

from .tws_app import TWSApp
from .util.logging import setup_logger
from .sim_trader.order import Order, OrderAction, OrderStatus


DEFAULT_ORDER_SIZE = 100

class CLIFront:
    
    def __init__(self):
        self.logger = setup_logger('sim_cli', None, logging.DEBUG, 'sim.log')
        self.tws_app = None
        self.app_thread = None
        self.order = None
        self.default_quantity = DEFAULT_ORDER_SIZE
        self.quantity_multiplier = 100
        self.console = Console()
        
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
        if not self._confirm_order_instant_exe(order):
            return
        self.tws_app.place_order(order)

    def _confirm_order_instant_exe(self, order: Order):
        if order.action == OrderAction.BUY:
            if order.limit is not None and order.limit > self.tws_app.tws_common.current_ask:
                self.console.print("[yellow]Instant execution because limit price is higher than the ask price! Proceed? [y/n]")
                if input().lower() != "y":
                    return False
            if order.stop is not None and order.stop < self.tws_app.tws_common.current_ask:
                self.console.print("[yellow]Instant execution because stop price is lower than the ask price! Proceed? [y/n]")
                if input().lower() != "y":
                    return False
        elif order.action == OrderAction.SELL:
            if order.limit is not None and order.limit < self.tws_app.tws_common.current_bid:
                self.console.print("[yellow]Instant execution because limit price is lower than the bid price! Proceed? [y/n]")
                if input().lower() != "y":
                    return False
            if order.stop is not None and order.stop > self.tws_app.tws_common.current_bid:
                self.console.print("[yellow]Instant execution because stop price is lower than the bid price! Proceed? [y/n]")
                if input().lower() != "y":
                    return False
        return True

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
                    self.tws_app.tws_common.portfolio.print_all_trades(self.console)
                elif args[1] == 'u':
                    self.tws_app.tws_common.portfolio.print_all_trades_unsorted(self.console)
                elif args[1] == "pos":
                    self.tws_app.tws_common.portfolio.print_positions(self.console)
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
                    self.tws_app.cancel_last_order()
                    return True
                if args[1] == 'a':
                    self.tws_app.cancel_all_orders()
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
                    return self._process_command([args[0][0], f"q{args[0][1:]}"] + args[1:])
                else:
                    print("Invalid command")
        return True
    
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
        for arg in args:
            if arg.startswith("q"):
                quantity = int(int(arg[1:]) * self.quantity_multiplier)
            elif arg.startswith("l"):
                limit = float(arg[1:])
            elif arg.startswith("st"):
                stop = float(arg[2:])
            else:
                limit = float(arg)
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
        self.console.rule("Commands")
        self.console.print("ls [green]Print all orders")
        self.console.print("ls pos [green]Print all orders or positions")
        self.console.print("set <default_quantity <quantity>> [green]Set the default quantity, default is 100")
        self.console.print("set <allow_short <1|0>> [green]Set 1 to allow short selling")
        self.console.print("track <symbol> [green]Track a symbol")
        self.console.print("b <q<quantity>> <l<limit>> [green]Buy the tracked symbol")
        self.console.print("s <q<quantity>> <l<limit>> [green]Sell the tracked symbol")
        self.console.print("st <q<quantity>> <l<limit>> [green]Set stop loss for the tracked symbol")
        self.console.print("cl [green]Close the current position for the tracked symbol")
        self.console.print("c <order_id> [green]Cancel an order")
        self.console.print("exit [green]Exit the program")
