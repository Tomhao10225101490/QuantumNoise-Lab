import json
import time
from dataclasses import asdict, dataclass

import qiskit
import qiskit_aer
from qiskit_aer import AerSimulator

from analysis.statistics import wilson
from quantum.circuits import raw_circuit, repetition_circuit
from quantum.noise_models import theory, validate


@dataclass(frozen=True)
class Config:
    p: float = 0.1
    c: float = 0.0
    m: float = 0.0
    state: int = 0
    shots: int = 8192
    seed: int = 2026

    def __post_init__(self):
        validate(self.p, self.c, self.m)
        if (
            self.state not in (0, 1)
            or not isinstance(self.shots, int)
            or not 1 <= self.shots <= 1000000
        ):
            raise ValueError("Invalid state or shots")
        if not isinstance(self.seed, int) or not 0 <= self.seed < 2**32:
            raise ValueError("seed must be a uint32")


def run(config):
    """Always executes Aer; caching, if desired, belongs to the caller."""
    cfg = config
    backend = AerSimulator(method="stabilizer", max_parallel_threads=1)
    rows = []
    for name, circuit, prediction in [
        ("raw", raw_circuit(cfg.p, cfg.state), cfg.p),
        (
            "encoded",
            repetition_circuit(cfg.p, cfg.c, cfg.m, cfg.state),
            theory(cfg.p, cfg.c, cfg.m),
        ),
    ]:
        start = time.perf_counter()
        result = backend.run(circuit, shots=cfg.shots, seed_simulator=cfg.seed).result()
        counts = result.get_counts()
        elapsed = time.perf_counter() - start
        errors = 0
        codeword_failures = 0
        syndromes = {format(s, "02b"): 0 for s in range(4)}
        for key, count in counts.items():
            if name == "encoded":
                output, report = key.split()
                syndromes[report] += count
                bit = int(output[-1])
                codeword_failures += count * (output != str(cfg.state) * 3)
            else:
                bit = int(key)
            errors += count * (bit != cfg.state)
        lo, hi = wilson(errors, cfg.shots)
        rows.append(
            {
                **asdict(cfg),
                "input_state": cfg.state,
                "model": name,
                "observed_errors": errors,
                "observed_error_rate": errors / cfg.shots,
                "theoretical_error_rate": prediction,
                "absolute_error": abs(errors / cfg.shots - prediction),
                "ci_low": lo,
                "ci_high": hi,
                "runtime": elapsed,
                "codeword_recovery_success_rate": 1 - codeword_failures / cfg.shots
                if name == "encoded"
                else None,
                "counts": json.dumps(counts, sort_keys=True),
                "syndrome_counts": json.dumps(syndromes),
                "qiskit_version": qiskit.__version__,
                "aer_version": qiskit_aer.__version__,
                "backend": "AerSimulator/stabilizer",
            }
        )
    return rows
