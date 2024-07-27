import json
import mplfinance as mpf
from pandas import DataFrame
import pandas as pd
import numpy as np
from betatrader import TrendAnalyser

with open('data/BBLG_1min_2024-07-24_extended.json', 'r') as f:
    data = json.load(f)
data = data[::-1]
df = DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
    
ta = TrendAnalyser()


for tick in data:
    ta.add_tick(tick)
    df.at[tick['date'], 'entry_signal'] = ta.klines[-1].entry_signal
    df.at[tick['date'], 'exit_signal'] = ta.klines[-1].exit_signal
    df.at[tick['date'], 'ema9'] = ta.klines[-1].ema9
    df.at[tick['date'], 'ema20'] = ta.klines[-1].ema20
    df.at[tick['date'], 'macd_signal'] = ta.klines[-1].macd_signal
    df.at[tick['date'], 'macd_curve'] = ta.klines[-1].macd_curve
    
apds = [ mpf.make_addplot(df['ema9'], color='r', secondary_y=False),
         mpf.make_addplot(df['ema20'], color='g', secondary_y=False),
         mpf.make_addplot(df['entry_signal'],type='scatter',markersize=100,marker='^', secondary_y=False),
         mpf.make_addplot(df['exit_signal'],type='scatter',markersize=100,marker='v', secondary_y=False),
         mpf.make_addplot(df['macd_signal'], color='b', secondary_y=False, panel=1),
            mpf.make_addplot(df['macd_curve'], color='y', secondary_y=False, panel=1)
       ]
mpf.plot(df, type='candle', addplot=apds, volume=False, style='yahoo')
mpf.show()


