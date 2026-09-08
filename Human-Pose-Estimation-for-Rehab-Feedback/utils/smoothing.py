# utils/smoothing.py
import numpy as np
from collections import deque

def moving_average(values, window=5):
    if len(values) < window:
        return values
    return np.convolve(values, np.ones(window)/window, mode="valid")

def ema_smoothing(values, alpha=0.7):
    """Exponential moving average smoothing (fast, adaptive)."""
    if not values:
        return []
    smoothed = []
    last = values[0]
    for v in values:
        last = alpha * v + (1 - alpha) * last
        smoothed.append(last)
    return smoothed

class SimpleSmoother:
    """Incremental moving average smoother (for streaming values)."""
    def __init__(self, window=5):
        self.q = deque(maxlen=window)

    def update(self, x):
        if x is None:
            return None
        self.q.append(float(x))
        return float(sum(self.q) / len(self.q))
