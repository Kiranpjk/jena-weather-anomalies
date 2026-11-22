# jena-weather-anomalies

[![CI](https://github.com/Kiranpjk/jena-weather-anomalies/actions/workflows/ci.yml/badge.svg)](https://github.com/Kiranpjk/jena-weather-anomalies/actions/workflows/ci.yml)
[![Docker](https://github.com/Kiranpjk/jena-weather-anomalies/actions/workflows/docker.yml/badge.svg)](https://github.com/Kiranpjk/jena-weather-anomalies/actions/workflows/docker.yml)
[![Report](https://github.com/Kiranpjk/jena-weather-anomalies/actions/workflows/report.yml/badge.svg)](https://github.com/Kiranpjk/jena-weather-anomalies/actions/workflows/report.yml)

Anomaly detection and forecasting baselines on **real hourly weather data for Jena, Germany**
(Open-Meteo archive API, 2023-2024, 17,544 hours of temperature and 10 m wind speed).
Built as a small, tested time-series project: data cleaning, a robust seasonal detector, a walk-forward backtest, CI and Docker.

## What it does

1. **Clean**: reindex to a strict hourly grid; interpolate gaps of up to 6 h; longer gaps stay missing so they are never mistaken for measurements.
2. **Detect**: for each hour of day, subtract the median of the surrounding 21 days (follows the seasons), then divide by a robust scale (MAD, shared by all hours). Points with |z| > 4 are flagged.
3. **Forecast baselines**: seasonal-naive and 7-day same-hour average, compared with a walk-forward backtest (24 h horizon, 60 origins).

## Run it

```bash
pip install -e ".[dev]"
python -m jena_anomalies.cli fetch      # optional: re-download data/jena_hourly.csv
python -m jena_anomalies.cli report
python -m jena_anomalies.cli report --html site/index.html   # same report as a static HTML page
pytest -q
```

`make install`, `make lint`, `make test`, `make report` and `make docker` wrap the same commands.
Optional: `pip install pre-commit && pre-commit install` runs ruff before each commit.

## Run with Docker

```bash
docker build -t jena-anomalies . && docker run --rm jena-anomalies
# or the image built by CI:
docker run --rm ghcr.io/kiranpjk/jena-weather-anomalies:latest
```

The image runs as a non-root user and contains the committed data file, so it needs no network.

## CI/CD

All in GitHub Actions (`.github/workflows/`):

- **ci.yml**: on every push to `main` and every pull request: `ruff check` and `pytest` on Python 3.10 and 3.12, with pip caching.
- **docker.yml**: on push to `main`: builds the Dockerfile and pushes `ghcr.io/kiranpjk/jena-weather-anomalies` tagged `latest` and the commit SHA, using the built-in `GITHUB_TOKEN`.
- **report.yml**: weekly (Monday) and on manual dispatch: runs the report on the committed CSV (no network fetch) and deploys the HTML to GitHub Pages.
  Pages has to be enabled once: **Settings → Pages → Source: GitHub Actions**.
- **Dependabot** checks pip dependencies and GitHub Actions versions weekly.

## Results on the real data (24 h horizon, 1,440 forecast hours)

| Series | Anomalies flagged (of 17,544 h) | Seasonal naive MAE | 7-day mean MAE |
|---|---|---|---|
| Temperature (°C) | 26 | 2.54 | 2.92 |
| Wind speed 10 m (km/h) | 46 | 4.84 | 4.81 |

Largest flagged wind values: 38.3 km/h (2023-03-10 23:00), 38.0 (2023-02-18 14:00), 37.5 (2024-10-10 07:00).
For temperature the simple "same as yesterday" beats the 7-day average; for wind the two are about equal, as expected for a series with little daily pattern.

## Tests

`pytest` covers parsing, gap handling, the detector (injected spikes are all found, a clean seasonal signal stays quiet, NaN is never flagged) and the forecasters (exact on periodic data, averaging beats naive on noise).
Writing them exposed two real bugs, both fixed:

- pandas `interpolate(limit=6)` also filled the first 6 hours of a *longer* gap; long gaps are now left fully missing.
- Estimating the MAD per hour of day (21 points each) was too noisy and gave about 17 false alarms where 4 spikes were injected; sharing one scale across all hours removed them.

## Limits

No ground truth for real anomalies: flagged hours are candidates, not confirmed events. The detector is univariate and uses a centered window, so it is for offline analysis, not live alerting.
