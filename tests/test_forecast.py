import numpy as np
import pandas as pd

from jena_anomalies.forecast import backtest, mean_of_days, seasonal_naive


def periodic(days=60):
    idx = pd.date_range("2024-01-01", periods=24 * days, freq="h")
    return pd.Series(np.tile(np.arange(24.0), days), index=idx)


def test_seasonal_naive_is_exact_on_periodic_data():
    s = periodic()
    assert backtest(s, seasonal_naive)["mae"] == 0.0


def test_mean_of_days_beats_seasonal_naive_on_noise():
    rng = np.random.default_rng(1)
    s = periodic(90) + pd.Series(rng.normal(0, 1, 24 * 90), index=periodic(90).index)
    assert backtest(s, mean_of_days)["mae"] < backtest(s, seasonal_naive)["mae"]


def test_horizon_longer_than_period():
    assert len(seasonal_naive(periodic(), 50)) == 50
