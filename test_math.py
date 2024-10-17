import json
import time
from betatrader.trendanalyser.common.maths import *
import matplotlib.pyplot as plt


first_ema_12 = 50.92781065617723
first_ema_26 = 50.0954916076672
first_dea = 0.7171

with open('data/APPL.json', 'r') as f:
    appl = json.load(f)
    
open_prices_r = np.array([day['open'] for day in appl['historical']][::-1])
close_prices_r = np.array([day['close'] for day in appl['historical']][::-1])
high_prices_r = np.array([day['high'] for day in appl['historical']][::-1])
low_prices_r = np.array([day['low'] for day in appl['historical']][::-1])
vol_r = np.array([day['volume'] for day in appl['historical']][::-1])

t = time.perf_counter()
ema_12 = ema_a(close_prices_r, first_ema_12, 12)
ema_26 = ema_a(close_prices_r, first_ema_26, 26)
macds = macd_a(ema_12, ema_26, first_dea)
print(f'Time taken: {time.perf_counter() - t}s')

t = time.perf_counter()
mavol_10 = ma_a(vol_r, 10)
print(f'Time taken: {time.perf_counter() - t}s')


# find 2024-06-01
for i, day in enumerate(appl['historical']):
    if day['date'] == '2024-06-03':
        break

t = time.perf_counter()
rsvs = rsv_a(close_prices_r, high_prices_r, low_prices_r, 9)
ks, ds, js = kdj_a(rsvs)
print(f'Time taken: {time.perf_counter() - t}s')



# plot dif in orange, dea in blue
plt.plot(macds[0], label='DIF', color='orange')
plt.plot(macds[1], label='DEA', color='blue')
for i, v in enumerate(macds[2]):
    if v > 0:
        plt.bar(i, v, color='g')
    else:
        plt.bar(i, v, color='r')
plt.legend()
plt.show()


# plot vol as bar chart
# plt.bar(range(len(vol)), vol)
# plt.plot(mavol_9, label='MAVOL 9')
# plt.legend()
# plt.show()