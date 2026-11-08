import json
from itertools import product

import pytest
from qiskit_aer import AerSimulator

from analysis.statistics import wilson
from quantum.circuits import repetition_circuit
from quantum.noise_models import correlation, distribution, theory
from quantum.simulator import Config, run
from quantum.syndrome import RECOVERY, syndrome


@pytest.mark.parametrize("p,c", list(product([0, 0.02, 0.1, 0.5], [0, 0.25, 1])))
def test_channel(p, c):
    dist = distribution(p, c)
    assert sum(dist.values()) == pytest.approx(1)
    assert min(dist.values()) >= 0
    for q in range(3):
        assert sum(
            prob for mask, prob in dist.items() if mask & (1 << q)
        ) == pytest.approx(p)
    assert theory(p, c) == pytest.approx((1 - c) * (3 * p * p - 2 * p**3) + c * 1.5 * p)
    assert correlation(p, c) >= 0


@pytest.mark.parametrize("state,mask", list(product([0, 1], range(8))))
def test_syndrome_recovery(state, mask):
    qc = repetition_circuit(0, state=state, forced_mask=mask)
    counts = AerSimulator().run(qc, shots=32, seed_simulator=1).result().get_counts()
    s = syndrome(mask)
    corrected = mask ^ ((1 << RECOVERY[s]) if s else 0)
    expected = format(corrected ^ (7 if state else 0), "03b") + " " + format(s, "02b")
    assert counts == {expected: 32}
    assert (corrected == 0) == (mask.bit_count() <= 1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"p": -0.1},
        {"p": 0.6},
        {"p": float("nan")},
        {"c": 1.1},
        {"m": -0.1},
        {"state": 2},
        {"shots": 0},
        {"seed": -1},
    ],
)
def test_validation(kwargs):
    with pytest.raises(ValueError):
        Config(**kwargs)


def test_endpoints():
    assert theory(0) == 0
    assert theory(0.5) == pytest.approx(0.5)
    rows = run(Config(p=0, shots=256))
    assert all(row["observed_errors"] == 0 for row in rows)


@pytest.mark.parametrize(
    "p,c,m", [(0.1, 0, 0), (0.25, 0.5, 0), (0.05, 0, 0.1), (0.5, 1, 0)]
)
def test_simulation_theory(p, c, m):
    for row in run(Config(p=p, c=c, m=m, shots=32768, seed=99)):
        lo, hi = wilson(row["observed_errors"], row["shots"], z=4)
        assert lo <= row["theoretical_error_rate"] <= hi


def test_reproducible_and_parameter_change():
    a = run(Config(shots=512))
    b = run(Config(shots=512))
    assert [r["counts"] for r in a] == [r["counts"] for r in b]
    changed = run(Config(p=0.5, shots=512))
    assert a[1]["counts"] != changed[1]["counts"]
    assert sum(json.loads(a[1]["syndrome_counts"]).values()) == 512
