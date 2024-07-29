import json
import mplfinance as mpf
from pandas import DataFrame
import pandas as pd
import numpy as np
from betatrader import TrendAnalyser

with open('data/intraday/AZTR_1min_2024-07-23_extended.json', 'r') as f:
    data = json.load(f)
data = data[::-1]
df = DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

ta = TrendAnalyser()
for tick in data:
    ta.add_tick(tick)
    df.at[tick['date'], 'ema9'] = ta.this_tick.fast_ema
    df.at[tick['date'], 'ema20'] = ta.this_tick.slow_ema
    df.at[tick['date'], 'ema_good'] = ta.this_tick.ema_good
    df.at[tick['date'], 'ema_death_cross'] = ta.this_tick.ema_death_cross
    df.at[tick['date'], 'ema_golden_cross'] = ta.this_tick.ema_golden_cross
    df.at[tick['date'], 'macd_signal'] = ta.this_tick.macd_signal
    df.at[tick['date'], 'macd_curve'] = ta.this_tick.macd_curve
    df.at[tick['date'], 'macd_good'] = ta.this_tick.macd_good
    df.at[tick['date'], 'macd_golden_cross'] = ta.this_tick.macd_golden_cross
    df.at[tick['date'], 'micro_pullback_likelihood'] = ta.this_tick.micro_pullback_likelihood
    df.at[tick['date'], 'entry_signal'] = ta.this_tick.entry_signal
    df.at[tick['date'], 'exit_signal'] = ta.this_tick.exit_signal
    df.at[tick['date'], 'reason'] = ta.this_tick.reason
    
df.to_csv('temp.csv')
    
apds = [ mpf.make_addplot(df['ema9'], color='r', secondary_y=False),
         mpf.make_addplot(df['ema20'], color='g', secondary_y=False),
         mpf.make_addplot(df['entry_signal'],type='scatter',markersize=100,marker='^',secondary_y=False,color='g',alpha=0.3),
         mpf.make_addplot(df['exit_signal'],type='scatter',markersize=100,marker='v',secondary_y=False,color='r',alpha=0.3),
         mpf.make_addplot(df['macd_signal'], color='b', secondary_y=False, panel=2),
            mpf.make_addplot(df['macd_curve'], color='y', secondary_y=False, panel=2)
       ]
mpf.plot(df, type='candle', addplot=apds, volume=True, style='yahoo')
mpf.show()


