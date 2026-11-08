"""Derive model-specific crossings and conservative pointwise benefit intervals."""

import json
from pathlib import Path

import pandas as pd
from scipy.optimize import brentq

from analysis.statistics import wilson
from quantum.noise_models import theory

ROOT = Path(__file__).resolve().parents[1]


def main():
    frame = pd.read_csv(ROOT / "results/processed/summary.csv")
    rows, crossings = [], []
    for keys, data in frame.groupby(["experiment", "c", "m", "input_state"]):
        pivot = data.pivot(index="p", columns="model")
        previous = None
        for p, values in pivot.iterrows():
            raw = values[("observed_error_rate", "raw")]
            encoded = values[("observed_error_rate", "encoded")]
            raw_ci = wilson(
                values[("observed_errors", "raw")],
                values[("shots", "raw")],
                z=2.241402727604947,
            )
            enc_ci = wilson(
                values[("observed_errors", "encoded")],
                values[("shots", "encoded")],
                z=2.241402727604947,
            )
            lower, upper = raw_ci[0] - enc_ci[1], raw_ci[1] - enc_ci[0]
            status = (
                "supported benefit"
                if lower > 0
                else "supported harm"
                if upper < 0
                else "unresolved"
            )
            rows.append(
                dict(zip(["experiment", "c", "m", "input_state"], keys, strict=True))
                | {
                    "p": p,
                    "benefit": raw - encoded,
                    "ci_low": lower,
                    "ci_high": upper,
                    "status": status,
                }
            )
            if previous and previous[1] * (raw - encoded) < 0:
                crossings.append(
                    dict(
                        zip(["experiment", "c", "m", "input_state"], keys, strict=True)
                    )
                    | {"observed_sign_change_bracket": [previous[0], p]}
                )
            previous = (p, raw - encoded)
    pd.DataFrame(rows).to_csv(ROOT / "results/processed/benefit.csv", index=False)
    roots = []
    for m in [0.01, 0.03, 0.05, 0.1]:
        root = brentq(
            lambda p, report_error=m: theory(p, 0, report_error) - p, 1e-10, 0.499999
        )
        roots.append(
            {
                "m": m,
                "theory_low_p_break_even": root,
                "predicted_benefit_open_interval": [root, 0.5],
            }
        )
    output = {
        "theoretical_crossings": roots,
        "observed_sign_change_brackets": crossings,
        "benefit_interval": "Difference of two 97.5% Wilson intervals; Bonferroni gives approximately 95% pointwise coverage. No across-grid multiplicity control. Brackets use point estimates, not confidence bounds.",
    }
    (ROOT / "results/processed/break_even.json").write_text(
        json.dumps(output, indent=2)
    )
    base = frame[
        (frame.experiment == "baseline") & (frame.input_state == 0) & (frame.p == 0.1)
    ].set_index("model")
    corr = frame[
        (frame.experiment == "correlated")
        & (frame.model == "encoded")
        & (frame.p == 0.1)
    ]
    paragraphs = [
        "# Measured findings",
        "",
        "Generated from results/processed/summary.csv. All rates below are Aer observations; analytical predictions are identified separately.",
        "",
        f"At p=0.10 and input |0>, unencoded error is {base.loc['raw', 'observed_error_rate']:.5f}; encoded independent error is {base.loc['encoded', 'observed_error_rate']:.5f}. Each estimate pools 24,576 shots across seeds 2026, 1701 and 31415.",
        "",
    ]
    for _, row in corr.iterrows():
        paragraphs.append(
            f"At p=0.10, c={row.c:.2f}: encoded error {row.observed_error_rate:.5f}, 95% Wilson [{row.ci_low:.5f}, {row.ci_high:.5f}]; exact theory {row.theoretical_error_rate:.5f}."
        )
    paragraphs += [
        "",
        "## Syndrome-cost crossings",
        "",
        "Only syndrome reports are noisy. The following low-p roots are analytical enumeration predictions, not universal thresholds. Observed sign-change brackets are saved in break_even.json; benefit.csv distinguishes supported benefit/harm from unresolved uncertainty.",
        "",
    ]
    for row in roots:
        paragraphs.append(
            f"m={row['m']:.2f}: theory predicts benefit for {row['theory_low_p_break_even']:.6f} < p < 0.5; below the lower crossing the model predicts harm."
        )
    paragraphs += [
        "",
        "## Limits",
        "",
        "Decoded-q0 Z error differs from whole-codeword recovery with faulty reports. No IBM hardware, arbitrary-state fidelity, phase protection, or fault-tolerant threshold claim. Same seed/configuration repetitions across experiment families are duplicated evidence and must not be pooled as independent trials. At p=0.5 the pair-mixture channel can have zero pairwise correlation while retaining higher-order dependence.",
    ]
    (ROOT / "docs/FINDINGS.md").write_text("\n\n".join(paragraphs) + "\n")
    print(
        "STAGE analysis: measured findings and crossing report complete; next validation"
    )


if __name__ == "__main__":
    main()
