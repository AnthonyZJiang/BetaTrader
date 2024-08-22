from ikbr_simulator import CLIFront
from ikbr_simulator.util.logutil import export_trade_from_log


front = CLIFront()
front.run()

# export_trade_from_log('.log/trade.log.csv', 'trades.csv', True)