from datetime import datetime
from ikbr_simulator.sim_trader.order import Order
from ikbr_simulator.sim_trader.portfolio import Portfolio

def export_trade_from_log(log_file: str, desitnation: str, today_only: bool = False):
    today = datetime.now().date()
    with open(log_file, 'r') as f:
        pf = Portfolio()
        date = None
        for line in f:
            order = Order.from_csv(line)
            if today_only and order.date_time.date() != today:
                continue
            if date is None:
                date = order.date_time.date()
            elif date != order.date_time.date():
                pf.export_trades(desitnation)
                pf = Portfolio()
                date = order.date_time.date()
            pf.add_order(order)
        
        pf.export_trades(desitnation)