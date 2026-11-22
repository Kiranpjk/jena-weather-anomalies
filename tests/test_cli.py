import numpy as np
import pandas as pd

from jena_anomalies.cli import main


def test_report_writes_html(tmp_path):
    idx = pd.date_range("2024-01-01", periods=24 * 60, freq="h", name="time")
    x = 10 + np.sin(np.arange(len(idx)) * 2 * np.pi / 24)
    x[500] = 60.0  # one obvious spike
    csv, out = tmp_path / "d.csv", tmp_path / "r.html"
    pd.DataFrame({"temperature_2m": x}, index=idx).to_csv(csv)
    main(["report", "--csv", str(csv), "--html", str(out)])
    page = out.read_text()
    assert "<h2>temperature_2m</h2>" in page
    assert "60.0" in page and "seasonal_naive" in page
