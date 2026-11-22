"""python -m jena_anomalies.cli fetch|report"""
import argparse
import html

from . import data, detect, forecast

MODELS = [("seasonal_naive", forecast.seasonal_naive), ("mean_of_7_days", forecast.mean_of_days)]


def analyse(df, threshold):
    """Per column: anomaly count, top-5 flagged values, backtest scores per baseline."""
    out = []
    for col in df.columns:
        s = df[col]
        flags = detect.detect(s, threshold)
        top = s[flags].sort_values(key=lambda x: (x - x.median()).abs(), ascending=False).head(5)
        out.append({"series": col, "anomalies": int(flags.sum()), "hours": int(s.notna().sum()),
                    "top": list(top.items()),
                    "scores": {name: forecast.backtest(s.dropna(), m) for name, m in MODELS}})
    return out


def to_html(results, threshold):
    e = html.escape
    parts = ["<!doctype html><html><head><meta charset='utf-8'><title>Jena weather anomalies</title>",
             ("<style>body{font-family:sans-serif;max-width:50em;margin:2em auto}"
              "table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:.3em .6em}</style>"),
             f"</head><body><h1>Jena weather anomalies</h1><p>Threshold |z| &gt; {threshold:g}</p>"]
    for r in results:
        parts.append(f"<h2>{e(r['series'])}</h2><p>{r['anomalies']} anomalies in {r['hours']} hours</p>")
        parts.append("<table><tr><th>Time</th><th>Value</th></tr>")
        parts += [f"<tr><td>{e(str(t))}</td><td>{v:.1f}</td></tr>" for t, v in r["top"]]
        parts.append("</table><table><tr><th>Baseline</th><th>MAE</th><th>RMSE</th><th>n</th></tr>")
        parts += [f"<tr><td>{e(n)}</td><td>{m['mae']:.2f}</td><td>{m['rmse']:.2f}</td><td>{m['n']}</td></tr>"
                  for n, m in r["scores"].items()]
        parts.append("</table>")
    parts.append("</body></html>")
    return "\n".join(parts)


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
    r.add_argument("--html", metavar="OUT", help="also write an HTML report to this path")
    a = p.parse_args(argv)

    if a.cmd == "fetch":
        df = data.fetch(a.start, a.end)
        df.to_csv(a.out)
        print(f"wrote {len(df)} rows to {a.out}")
        return
    results = analyse(data.load(a.csv), a.threshold)
    for r in results:
        print(f"\n== {r['series']}: {r['anomalies']} anomalies in {r['hours']} hours")
        for t, v in r["top"]:
            print(f"   {t}  {v:.1f}")
        for name, m in r["scores"].items():
            print(f"   {name:15s}", m)
    if a.html:
        with open(a.html, "w", encoding="utf-8") as fh:
            fh.write(to_html(results, a.threshold))
        print(f"\nwrote HTML report to {a.html}")

if __name__ == "__main__":
    main()
