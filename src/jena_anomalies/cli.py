"""python -m jena_anomalies.cli fetch|report"""
import argparse

from . import data, detect, forecast


def main(argv=None):
    p = argparse.ArgumentParser(prog="jena-anomalies")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="download hourly data to a CSV")
    f.add_argument("--start", default="2023-01-01")
    f.add_argument("--end", default="2024-12-31")
    f.add_argument("--out", default="data/jena_hourly.csv")
    r = sub.add_parser("report", help="detect anomalies and compare forecast baselines")
    r.add_argument("--csv", default="data/jena_hourly.csv")
    r.add_argument("--threshold", type=float, default=4.0)
    a = p.parse_args(argv)

    if a.cmd == "fetch":
        df = data.fetch(a.start, a.end)
        df.to_csv(a.out)
        print(f"wrote {len(df)} rows to {a.out}")
        return
    df = data.load(a.csv)
    for col in df.columns:
        s = df[col]
        flags = detect.detect(s, a.threshold)
        print(f"\n== {col}: {int(flags.sum())} anomalies in {int(s.notna().sum())} hours")
        for t, v in s[flags].sort_values(key=lambda x: (x - x.median()).abs(), ascending=False).head(5).items():
            print(f"   {t}  {v:.1f}")
        for name, m in [("seasonal_naive", forecast.seasonal_naive), ("mean_of_7_days", forecast.mean_of_days)]:
            print(f"   {name:15s}", forecast.backtest(s.dropna(), m))


if __name__ == "__main__":
    main()
