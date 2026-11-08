"""Rebuild the complete evidence bundle: python -m experiments.run_all."""

import hashlib
import json
import platform
from datetime import UTC, datetime
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis.plotting import benefit_heatmap, comparison
from analysis.statistics import wilson
from quantum.circuits import repetition_circuit
from quantum.simulator import Config, run

ROOT = Path(__file__).resolve().parents[1]
P = [0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
SEEDS = [2026, 1701, 31415]


def aggregate(raw):
    records = []
    for keys, frame in raw.groupby(
        ["experiment", "p", "c", "m", "input_state", "model"]
    ):
        shots, errors = int(frame.shots.sum()), int(frame.observed_errors.sum())
        lo, hi = wilson(errors, shots)
        records.append(
            dict(
                zip(
                    ["experiment", "p", "c", "m", "input_state", "model"],
                    keys,
                    strict=True,
                )
            )
            | {
                "shots": shots,
                "observed_errors": errors,
                "observed_error_rate": errors / shots,
                "theoretical_error_rate": frame.theoretical_error_rate.iloc[0],
                "ci_low": lo,
                "ci_high": hi,
                "seed_count": len(frame),
                "runtime": frame.runtime.sum(),
            }
        )
    return pd.DataFrame(records)


def main():
    rows = []
    for experiment, cs, ms, states in [
        ("baseline", [0], [0], [0, 1]),
        ("correlated", [0, 0.25, 0.5, 0.75, 1], [0], [0]),
        ("break_even", [0], [0, 0.01, 0.03, 0.05, 0.1], [0]),
    ]:
        for p in P:
            for c in cs:
                for m in ms:
                    for state in states:
                        for seed in SEEDS:
                            rows.extend(
                                dict(experiment=experiment, **r)
                                for r in run(Config(p, c, m, state, 8192, seed))
                            )
        print(
            f"STAGE {experiment}: Aer complete; {len(rows)} cumulative rows; blockers none",
            flush=True,
        )
    raw = pd.DataFrame(rows)
    summary = aggregate(raw)
    raw.to_csv(ROOT / "results/raw/experiments.csv", index=False)
    summary.to_csv(ROOT / "results/processed/summary.csv", index=False)
    charts = {
        "figure1_theory": comparison(
            summary[(summary.experiment == "baseline") & (summary.input_state == 0)]
        ),
        "figure2_encoded": comparison(
            summary[(summary.experiment == "baseline") & (summary.input_state == 1)],
            title="Encoded vs unencoded · input |1⟩",
        ),
        "figure3_correlated": comparison(
            summary[
                (summary.experiment == "correlated") & (summary.model == "encoded")
            ],
            "c",
            "Correlated pairs destroy majority protection",
        ),
        "figure4_benefit": benefit_heatmap(summary[summary.experiment == "correlated"]),
        "figure5_recovery": comparison(
            summary[
                (summary.experiment == "break_even") & (summary.model == "encoded")
            ],
            "m",
            "Noisy syndrome reports · decoded q0",
        ),
    }
    for name, chart in charts.items():
        chart.write_html(ROOT / f"results/figures/{name}.html", include_plotlyjs=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    base = summary[(summary.experiment == "baseline") & (summary.input_state == 0)]
    for model, frame in base.groupby("model"):
        ax.errorbar(
            frame.p,
            frame.observed_error_rate,
            yerr=[
                frame.observed_error_rate - frame.ci_low,
                frame.ci_high - frame.observed_error_rate,
            ],
            fmt="o",
            capsize=3,
            label=f"{model}: Aer, 95% Wilson",
        )
        ax.plot(frame.p, frame.theoretical_error_rate, "--", label=f"{model}: theory")
    ax.set(
        xlabel="Physical X-error probability p",
        ylabel="Output Z-error probability",
        title="QuantumNoise Lab · measured evidence",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/baseline.png", dpi=180)
    plt.close(fig)
    for name, kwargs in [("ideal", {}), ("noisy_syndrome", {"m": 0.03})]:
        qc = repetition_circuit(0.1, **kwargs)
        qc.draw(
            output="mpl",
            fold=70,
            filename=str(ROOT / f"results/figures/circuit_{name}.png"),
        )
        (ROOT / f"results/figures/circuit_{name}.txt").write_text(
            str(qc.draw(output="text", fold=110))
        )
        plt.close("all")
    hashes = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in ROOT.glob("results/**/*.csv")
    }
    metadata = {
        "created_utc": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "qiskit": raw.qiskit_version.iloc[0],
        "aer": raw.aer_version.iloc[0],
        "shots_per_point": 8192,
        "seeds": SEEDS,
        "p_grid": P,
        "c_grid": [0, 0.25, 0.5, 0.75, 1],
        "m_grid": [0, 0.01, 0.03, 0.05, 0.1],
        "backend": "AerSimulator/stabilizer",
        "hardware": False,
        "rows": len(raw),
        "total_shots": int(raw.shots.sum()),
        "csv_sha256": hashes,
        "noise": "(1-c) IID Bernoulli(p) + c pair channel: P(000)=1-3p/2, P(each pair)=p/2",
        "uncertainty": "Pointwise 95% Wilson; pooled across three seeds; not simultaneous bands",
    }
    (ROOT / "results/processed/configuration.json").write_text(
        json.dumps(metadata, indent=2)
    )
    findings = summary[(summary.p == 0.1) & (summary.input_state == 0)].to_dict(
        orient="records"
    )
    (ROOT / "results/processed/findings.json").write_text(
        json.dumps(findings, indent=2)
    )
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
