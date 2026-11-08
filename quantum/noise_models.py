"""Explicit, fixed-marginal Pauli-X channels. Masks use q0 as bit 0."""

import math
from itertools import product

from qiskit_aer.noise import pauli_error


def validate(p, c=0.0, m=0.0):
    for name, value, upper in [("p", p, 0.5), ("c", c, 1), ("m", m, 0.5)]:
        if not math.isfinite(value) or not 0 <= value <= upper:
            raise ValueError(f"{name} must be finite and in [0, {upper}]")


def distribution(p, c=0.0):
    validate(p, c)
    independent = {
        mask: p ** mask.bit_count() * (1 - p) ** (3 - mask.bit_count())
        for mask in range(8)
    }
    pair = dict.fromkeys(range(8), 0.0)
    pair.update({0: 1 - 1.5 * p, 3: p / 2, 5: p / 2, 6: p / 2})
    return {mask: (1 - c) * independent[mask] + c * pair[mask] for mask in range(8)}


def channel(p, c=0.0):
    return pauli_error(
        [
            ("".join("X" if mask & (1 << q) else "I" for q in reversed(range(3))), prob)
            for mask, prob in distribution(p, c).items()
            if prob > 0
        ]
    )


def theory(p, c=0.0, m=0.0):
    """Exact output-q0 Z error, enumerating data errors and syndrome report flips."""
    validate(p, c, m)
    rate = 0.0
    for mask, probability in distribution(p, c).items():
        e = [(mask >> q) & 1 for q in range(3)]
        s = (e[0] ^ e[1]) | ((e[1] ^ e[2]) << 1)
        for a, b in product(range(2), repeat=2):
            report = s ^ a ^ (b << 1)
            rate += (
                probability
                * m ** (a + b)
                * (1 - m) ** (2 - a - b)
                * (e[0] ^ (report == 1))
            )
    return rate


def correlation(p, c):
    validate(p, c)
    return 0.0 if p == 0 else c * (p / 2 - p * p) / (p * (1 - p))
