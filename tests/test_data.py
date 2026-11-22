import numpy as np
import pandas as pd

from jena_anomalies.data import clean, parse


def test_parse_open_meteo_payload():
    payload = {"hourly": {"time": ["2024-01-01T00:00", "2024-01-01T01:00"],
                          "temperature_2m": [1.0, 2.0], "wind_speed_10m": [3.0, 4.0]}}
    df = parse(payload)
    assert list(df.columns) == ["temperature_2m", "wind_speed_10m"]
    assert df.index[1] - df.index[0] == pd.Timedelta("1h")


def test_clean_fills_short_gap_but_keeps_long_gap_missing():
    idx = pd.date_range("2024-01-01", periods=40, freq="h")
    df = pd.DataFrame({"x": np.arange(40.0)}, index=idx).drop(idx[[5, 6]]).drop(idx[20:30])
    out = clean(df)
    assert out["x"].iloc[5] == 5.0  # 2 h gap interpolated
    assert out["x"].iloc[20:26].isna().all()  # gap longer than 6 h is not invented
