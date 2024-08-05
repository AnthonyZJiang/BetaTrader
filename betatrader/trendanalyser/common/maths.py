import numpy as np

def ma_a(values: np.array, period: int) -> np.array:
    """Calculate Simple Moving Average"""
    n = len(values)
    mas = np.zeros(n)
    for i in range(1,n):
        if i >= period:
            ma = ma + (values[i] - values[i-period])/period
        else:
            ma = np.mean(values[:i+1])
            
        mas[i] = ma
    return mas

def ema(value: float, prev_ema: float, period: int, k: int = None) -> float:
    """Calculate Exponential Moving Average"""
    if k is None:
        k = 2 / (period + 1)
    return value * k + prev_ema * (1 - k)

def ema_a(values: np.array, first_ema: int, period: int, k: int = None) -> np.array:
    """Calculate Exponential Moving Averages using numpy"""
    n = len(values)
    emas = np.zeros(n)
    if k is None:
        k = 2 / (period + 1)
    emas[0] = first_ema
    for i in range(n-1):
        emas[i+1] = values[i+1] * k + emas[i] * (1 - k)
    return emas

def sma(value: float, prev_sma: float, period: int, weight: int) -> float:
    """Calculate Simple Moving Average"""
    return (value * weight + prev_sma * (period - weight)) / period

def sma_a(values: np.array, period: int, weight: int, first_sma: int) -> np.array:
    """Calculate Simple Moving Average"""
    n = len(values)
    smas = np.zeros(n)
    smas[0] = first_sma
    for i in range(n-1):
        smas[i+1] = (values[i+1] * weight + smas[i] * (period - weight)) / period
    return smas

def macd_a(fast_ema: np.array, slow_ema: np.array, first_dea: float) -> tuple[np.array, np.array, np.array]:
    diffs = fast_ema - slow_ema
    deas = ema_a(diffs, first_dea, 9)
    macds = (diffs - deas) * 2
    return diffs, deas, macds

def rsv_a(closing_prices: np.array, high_prices:np.array, low_prices:np.array, period:int) -> np.array:
    """Calculate Relative Strength Value"""
    n = len(closing_prices)
    rsvs = np.zeros(n)
    for i in range(n):
        i_1 = i - period
        if i_1 < 0:
            i_1 = 0
        highest = max(high_prices[i_1:i+1])
        lowest = min(low_prices[i_1:i+1])
        rsvs[i] = (closing_prices[i] - lowest) / (highest - lowest) * 100
        
    return rsvs

def kdj_a(rsv9: np.array, k1: int = 50, d1: int = 50) -> np.array:
    """Calculate KDJ"""
    n = len(rsv9)
    ks = np.zeros(n)
    ds = np.zeros(n)
    js = np.zeros(n)
    ks[0] = k1
    ds[0] = d1
    for i in range(1,n):
        ks[i] = 2/3 * ks[i-1] + 1/3 * rsv9[i]
        ds[i] = 2/3 * ds[i-1] + 1/3 * ks[i]
    ks = sma_a(rsv9, 3, 1, k1)
    ds = sma_a(ks, 3, 1, d1)
    js = ks * 3 - ds * 2
    return ks, ds, js

def reverse_list(lst: list) -> list:
    """Reverse a list"""
    return lst[::-1]