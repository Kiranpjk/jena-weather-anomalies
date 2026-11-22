"""Fetch and clean hourly weather for Jena from the Open-Meteo archive API (no API key)."""
import json
import urllib.request

import pandas as pd

URL = (
    "https://archive-api.open-meteo.com/v1/archive?latitude=50.93&longitude=11.59"
    "&start_date={start}&end_date={end}&hourly=temperature_2m,wind_speed_10m&timezone=UTC"
)


def parse(payload: dict) -> pd.DataFrame:
    """Open-Meteo JSON -> hourly DataFrame indexed by UTC time."""
    h = payload["hourly"]
    df = pd.DataFrame({k: h[k] for k in h if k != "time"}, index=pd.to_datetime(h["time"]))
    df.index.name = "time"
    return df


def clean(df: pd.DataFrame, max_gap: int = 6) -> pd.DataFrame:
    """Reindex to a strict hourly grid and interpolate gaps up to `max_gap` hours.

    Longer gaps stay NaN so they are never mistaken for real measurements.
    """
    grid = pd.date_range(df.index.min(), df.index.max(), freq="h", name="time")
    out = df[~df.index.duplicated()].reindex(grid)
    filled = out.interpolate(limit_area="inside")
    for col in out:  # pandas `limit` would fill the first hours of a long gap; blank whole long gaps instead
        miss = out[col].isna()
        run = miss.groupby((~miss).cumsum()).transform("sum")
        filled.loc[miss & (run > max_gap), col] = float("nan")
    return filled


def fetch(start: str, end: str) -> pd.DataFrame:
    with urllib.request.urlopen(URL.format(start=start, end=end), timeout=60) as r:
        return clean(parse(json.load(r)))


def load(path: str) -> pd.DataFrame:
    return pd.read_csv(path, index_col="time", parse_dates=True)
