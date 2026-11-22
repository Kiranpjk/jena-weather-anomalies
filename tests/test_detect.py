import numpy as np
import pandas as pd

from jena_anomalies.detect import detect


def synthetic(n_days=120, seed=0):
    idx = pd.date_range("2024-01-01", periods=24 * n_days, freq="h")
    rng = np.random.default_rng(seed)
    daily = 5 * np.sin(2 * np.pi * (idx.hour - 9) / 24)
    drift = np.linspace(0, 8, len(idx))
    return pd.Series(10 + daily + drift + rng.normal(0, 0.5, len(idx)), index=idx)


def test_finds_injected_spikes_with_few_false_alarms():
    s = synthetic()
    spikes = s.index[[500, 1200, 2000, 2500]]
    s[spikes] += 15
    flags = detect(s)
    assert flags[spikes].all()  # recall 100 %
    assert flags.sum() <= len(spikes) + 3  # at most a few false alarms in 2880 points


def test_clean_seasonal_signal_is_quiet():
    assert detect(synthetic()).mean() < 0.005


def test_nan_is_never_flagged():
    s = synthetic()
    s.iloc[100:110] = np.nan
    assert not detect(s).iloc[100:110].any()
