import yfinance as yf
import json

aztr = yf.Ticker("AZTR")
hist = aztr.history(period='1d', interval='1m', start='2024-07-23', end='2024-07-24', prepost=True)
data = json.loads(hist.to_json(orient='table'))
with open('data/AZTR_1d_1m_2024-07-23_2024-07-23_extended.json', 'w') as f:
    json.dump(data, f, indent=4)

