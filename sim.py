from ikbr_simulator import CLIFront
from ikbr_simulator.util.logutil import export_trade_from_log
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        export_trade_from_log('.log/trade.log.csv', 'tradesviz.csv', True)
        print('Exported trades to trades.csv')
    else:
        front = CLIFront()
        front.run()