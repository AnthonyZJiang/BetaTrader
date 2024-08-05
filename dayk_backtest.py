import json
import pandas as pd
from pandas import DataFrame
import mplfinance as mpf

import numpy as np
from scipy.interpolate import BSpline, splrep, splev
import matplotlib.pyplot as plt

from betatrader.trendanalyser.common.kline import KlineBar
from betatrader.trendanalyser.common.indicator import *


symbol = 'AMZN'
with open(f'data/{symbol}_1day_2010-01-01.json', 'r') as f:
    data = json.load(f)
    
data = data[::-1]
df = DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

bars = []

x = []
y = []

prev_macd = 0
prev_kdj  = 0
prev_rsi  = 0

ema_cal = EMACalculator([9,20,60,200])
macd_cal = MACDCalculator()
kdj_cal = KDJCalculator()
rsi_cal = RSICalculator([6,12,24])
signal = 0
confirmation = 0
for i, bar_data in enumerate(data):
    bar = KlineBar(bar_data, i)
    bars.append(bar)
    ema_cal.calculate(bars)
    macd_cal.calculate(bars)
    kdj_cal.calculate(bars)
    rsi_cal.calculate(bars)
    
    df.at[bar_data['date'], 'ema9'] = bar.indicators['ema'].values[9]
    df.at[bar_data['date'], 'ema20'] = bar.indicators['ema'].values[20]
    df.at[bar_data['date'], 'ema60'] = bar.indicators['ema'].values[60]
    df.at[bar_data['date'], 'ema200'] = bar.indicators['ema'].values[200]
    df.at[bar_data['date'], 'macd_curve'] = bar.indicators['macd'].curve
    df.at[bar_data['date'], 'macd_signal'] = bar.indicators['macd'].signal
    df.at[bar_data['date'], 'macd'] = bar.indicators['macd'].macd
    df.at[bar_data['date'], 'kdj_k'] = bar.indicators['kdj'].k
    df.at[bar_data['date'], 'kdj_d'] = bar.indicators['kdj'].d
    df.at[bar_data['date'], 'kdj_j'] = bar.indicators['kdj'].j
    df.at[bar_data['date'], 'rsi6'] = bar.indicators['rsi'].values[6]
    df.at[bar_data['date'], 'rsi12'] = bar.indicators['rsi'].values[12]
    df.at[bar_data['date'], 'rsi24'] = bar.indicators['rsi'].values[24]
    mid = (bar.data.open + bar.data.close)/2
    
    if confirmation >= 3:
        df.at[bar_data['date'], 'entry_confirmed'] = bar.data.low
        confirmation = 0
        
    if signal >= 5:
        confirmation = 0
        df.at[bar_data['date'], 'entry_signal'] = bar.data.low
        if prev_macd < bar.indicators['macd'].macd:
            confirmation += 1
        if bar.indicators['kdj'].j > max(bar.indicators['kdj'].d, bar.indicators['kdj'].k):
            confirmation += 1
        if bar.indicators['rsi'].values[6] > max(bar.indicators['rsi'].values[12], bar.indicators['rsi'].values[24]):
            confirmation += 1
            
    if i > 0:
        signal = 0
        if prev_macd < bar.indicators['macd'].macd:
            signal += 1
        this_kdj = bar.indicators['kdj'].j > bar.indicators['kdj'].k > bar.indicators['kdj'].d
        if prev_kdj and this_kdj:
            signal += 1
        this_rsi = bar.indicators['rsi'].values[6] > max(bar.indicators['rsi'].values[12], bar.indicators['rsi'].values[24])
        if prev_rsi and this_rsi:
            signal += 1
        if bar.indicators['rsi'].values[6] < 65:
            signal += 1
        if bar.indicators['kdj'].j < 80:
            signal += 1
        
    
    prev_macd = bar.indicators['macd'].macd
    prev_kdj = bar.indicators['kdj'].d > bar.indicators['kdj'].k > bar.indicators['kdj'].j
    prev_rsi = bar.indicators['rsi'].values[24] > bar.indicators['rsi'].values[12] > bar.indicators['rsi'].values[6]
    
    x.append(i)
    y.append(mid)
    
# df.to_csv('temp.csv')
ts = np.array(x)
ys = np.array(y)

n_interior_knots = len(ts) // 30
qs = np.linspace(0, 1, n_interior_knots+2)[1:-1]
knots = np.quantile(ts, qs)
tck = splrep(ts, ys, t=knots, k=3)
ys_smooth = splev(ts, tck)

# plt.figure(figsize=(12, 6))
# plt.plot(ts, ys, '.c')
# plt.plot(ts, ys_smooth, '-m')
# plt.show()

for i, bar_data in enumerate(data):
    df.at[bar_data['date'], 'smooth'] = ys_smooth[i]

apds = [ mpf.make_addplot(df['ema9'], color='r', secondary_y=False),
         mpf.make_addplot(df['ema20'], color='orange', secondary_y=False),
        #  mpf.make_addplot(df['ema60'], color='g', secondary_y=False),
        #  mpf.make_addplot(df['ema200'], color='b', secondary_y=False),
        # mpf.make_addplot(df['smooth'], color='b', secondary_y=False),
         mpf.make_addplot(df['rsi6'], color='r', secondary_y=False, panel=3),
        mpf.make_addplot(df['rsi12'], color='orange', secondary_y=False, panel=3),
        mpf.make_addplot(df['rsi24'], color='g', secondary_y=False, panel=3),
        mpf.make_addplot(df['kdj_k'], color='r', secondary_y=False, panel=2),
        mpf.make_addplot(df['kdj_d'], color='orange', secondary_y=False, panel=2),
        mpf.make_addplot(df['kdj_j'], color='g', secondary_y=False, panel=2),
         mpf.make_addplot(df['entry_signal'],type='scatter',markersize=100,marker='^',secondary_y=False,color='g',alpha=0.3)
        #  mpf.make_addplot(df['exit_signal'],type='scatter',markersize=100,marker='v',secondary_y=False,color='r',alpha=0.3),
        #  mpf.make_addplot(df['macd_signal'], color='b', secondary_y=False, panel=2),
        #     mpf.make_addplot(df['macd_curve'], color='y', secondary_y=False, panel=2)
       ]
if 'entry_confirmed' in df.columns:
    apds.append(mpf.make_addplot(df['entry_confirmed'],type='scatter',markersize=100,marker='^',secondary_y=False,color='r',alpha=0.3))
mpf.plot(df, type='candle', addplot = apds, volume=True, style='yahoo')
mpf.show()