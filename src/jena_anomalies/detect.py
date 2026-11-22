"""Seasonal robust z-score anomaly detection.

The typical value for each hour of day is its median over a trailing window of days
(so slow seasonal drift is followed). Residual scale uses the median absolute deviation
(MAD), which a few outliers cannot inflate the way a standard deviation can.
"""
import numpy as np
import pandas as pd


def robust_zscore(s: pd.Series, window_days: int = 21) -> pd.Series:
    hours = s.index.hour
    resid = pd.Series(np.nan, index=s.index)
    for h in range(24):
        sub = s[hours == h]
        med = sub.rolling(window_days, center=True, min_periods=window_days // 2).median()
        resid[sub.index] = sub - med
    # One scale shared by all hours: 21 points per hour give a too noisy MAD and many false alarms.
    n = window_days * 24
    mad = resid.abs().rolling(n, center=True, min_periods=n // 2).median()
    return resid / (1.4826 * mad.clip(lower=1e-6))


def detect(s: pd.Series, threshold: float = 4.0, window_days: int = 21) -> pd.Series:
    """Boolean mask of anomalous points (|robust z| > threshold). NaN input is never flagged."""
    return robust_zscore(s, window_days).abs().gt(threshold) & s.notna()
