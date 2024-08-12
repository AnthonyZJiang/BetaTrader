from ikbr_simulator import SimulatorCLI
from ikbr_simulator.util.logutility import export_trade_from_log


sim = SimulatorCLI()
sim.run()

export_trade_from_log('.log/trade.log.csv', 'trades.csv', True)