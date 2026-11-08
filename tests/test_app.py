import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "page",
    [
        "Overview",
        "Interactive Noise Lab",
        "Quantum Circuit Explorer",
        "Noise Comparison",
        "Research Findings",
    ],
)
def test_pages(page):
    app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=30).run()
    app.radio[0].set_value(page).run()
    assert not app.exception


def test_live_cache_and_fresh():
    app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=30).run()
    app.radio[0].set_value("Interactive Noise Lab").run()
    app.button[0].click().run()
    assert not app.exception
    assert "FRESH EXECUTION" in app.success[0].value
    first = app.session_state["last_result"][0][1]["counts"]
    app.button[0].click().run()
    assert "CACHE HIT" in app.success[0].value
    app.slider[0].set_value(0.4)
    app.button[0].click().run()
    assert not app.exception
    assert "FRESH EXECUTION" in app.success[0].value
    assert first != app.session_state["last_result"][0][1]["counts"]


def test_csv_provenance():
    raw = pd.read_csv(ROOT / "results/raw/experiments.csv")
    summary = pd.read_csv(ROOT / "results/processed/summary.csv")
    metadata = json.loads((ROOT / "results/processed/configuration.json").read_text())
    assert len(raw) == metadata["rows"]
    assert int(raw.shots.sum()) == metadata["total_shots"]
    for filename, expected in metadata["csv_sha256"].items():
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == expected
    grouped = raw.groupby(["experiment", "p", "c", "m", "input_state", "model"])
    for _, row in summary.iterrows():
        group = grouped.get_group(tuple(row[k] for k in grouped.keys))
        assert row.observed_error_rate == pytest.approx(
            group.observed_errors.sum() / group.shots.sum()
        )
        assert row.ci_low <= row.observed_error_rate <= row.ci_high


def test_force_fresh_override():
    app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=30).run()
    app.radio[0].set_value("Interactive Noise Lab").run()
    app.button[0].click().run()
    app.checkbox[0].set_value(True)
    app.button[0].click().run()
    assert not app.exception
    assert "FRESH EXECUTION" in app.success[0].value
