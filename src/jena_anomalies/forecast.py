"""Baseline forecasters and a rolling-origin backtest."""
import numpy as np
import pandas as pd


def seasonal_naive(history: pd.Series, horizon: int, period: int = 24) -> np.ndarray:
    """Repeat the last full season."""
    last = history.to_numpy()[-period:]
    return np.tile(last, int(np.ceil(horizon / period)))[:horizon]


def mean_of_days(history: pd.Series, horizon: int, period: int = 24, days: int = 7) -> np.ndarray:
    """Average the same hour over the last `days` seasons."""
    v = history.to_numpy()[-period * days:].reshape(-1, period)
    return np.tile(np.nanmean(v, axis=0), int(np.ceil(horizon / period)))[:horizon]


def backtest(s: pd.Series, model, horizon: int = 24, folds: int = 60, step: int = 24 * 5) -> dict:
    """Walk-forward evaluation: forecast `horizon` hours from `folds` origins, return MAE and RMSE."""
    errs = []
    for i in range(folds):
        end = len(s) - horizon - i * step
        if end < 24 * 14:
            break
        pred = model(s.iloc[:end], horizon)
        true = s.iloc[end:end + horizon].to_numpy()
        errs.append(pred - true)
    e = np.concatenate(errs)
    e = e[~np.isnan(e)]
    return {"mae": float(np.abs(e).mean()), "rmse": float(np.sqrt((e ** 2).mean())), "n": int(e.size)}
