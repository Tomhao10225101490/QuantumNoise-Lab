from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer.noise import pauli_error

from quantum.noise_models import channel, validate
from quantum.syndrome import RECOVERY


def raw_circuit(p, state=0):
    validate(p)
    if state not in (0, 1):
        raise ValueError("state must be 0 or 1")
    qc = QuantumCircuit(1, 1, name="Unencoded")
    if state:
        qc.x(0)
    qc.append(pauli_error([("X", p), ("I", 1 - p)]).to_instruction(), [0])
    qc.measure(0, 0)
    return qc


def repetition_circuit(p, c=0.0, m=0.0, state=0, forced_mask=None):
    validate(p, c, m)
    if state not in (0, 1):
        raise ValueError("state must be 0 or 1")
    if forced_mask is not None and forced_mask not in range(8):
        raise ValueError("forced_mask must be in range(8)")
    data, anc = QuantumRegister(3, "data"), QuantumRegister(2, "anc")
    syn, out = ClassicalRegister(2, "s"), ClassicalRegister(3, "out")
    qc = QuantumCircuit(data, anc, syn, out, name="Repetition code")
    if state:
        qc.x(data[0])
    qc.cx(data[0], data[1])
    qc.cx(data[0], data[2])
    qc.barrier(label="Encode")
    if forced_mask is None:
        qc.append(channel(p, c).to_instruction(), data)
    else:
        for q in range(3):
            if forced_mask & (1 << q):
                qc.x(data[q])
    qc.barrier(label="Noise")
    qc.cx(data[0], anc[0])
    qc.cx(data[1], anc[0])
    qc.cx(data[1], anc[1])
    qc.cx(data[2], anc[1])
    for q in range(2):
        if m:
            qc.append(pauli_error([("X", m), ("I", 1 - m)]).to_instruction(), [anc[q]])
        qc.measure(anc[q], syn[q])
    qc.barrier(label="Syndrome")
    for report, target in RECOVERY.items():
        with qc.if_test((syn, report)):
            qc.x(data[target])
    qc.barrier(label="Recover")
    qc.measure(data, out)
    return qc
