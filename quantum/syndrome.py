"""s0=q0 XOR q1; s1=q1 XOR q2; integer s=s0+2*s1."""

RECOVERY = {1: 0, 3: 1, 2: 2}


def syndrome(mask):
    e = [(mask >> q) & 1 for q in range(3)]
    return (e[0] ^ e[1]) | ((e[1] ^ e[2]) << 1)
