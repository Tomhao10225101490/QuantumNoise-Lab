# Project progress and decisions

Updated November 8, 2026, Asia/Shanghai. Work started in a new empty QFF2026 workspace and is isolated in QuantumNoise-Lab.

## Completed

- P0: Actual Qiskit/Aer execution; three data qubits, two measured ancillas, conditional X recovery; all eight injected X patterns checked for both basis inputs.
- P1: Fixed-marginal independent/pair-mixture noise; explicit normalized distribution and correlation definition; five mixture strengths; real raw counts and confidence intervals.
- P2: Five Streamlit views; true live subprocess Aer execution; explicit session cache labels; circuit drawings; raw data downloads; five offline Plotly figures; README, English Devpost text and three-minute script.
- P3: Independent syndrome-report error model; exact enumeration and measured break-even brackets; uncertainty-aware benefit classifications.
- Full evidence: 720 circuit runs, 5,898,240 shots, three seeds and ten p values. These totals describe the saved sweep; deterministic validation and interactive jobs are additional executions.
- Validation: 50 pytest tests passed, compilation passed, Ruff passed. Browser verified overview, real fresh Aer execution, cache reuse, correlation charts, and circuit explorer. Matplotlib circuit image was visually inspected.

## Decisions

Use Python 3.12 in a fresh venv, Qiskit 2.6.2, Aer 0.18.2, pinned installed requirements. Use stabilizer simulation because all gates are Clifford and channels are Pauli. Preserve p under correlation changes by mixing an independent channel with a symmetric pair-flip channel. Report decoded-q0 Z error separately from whole-codeword recovery. Use Wilson intervals and separate analytical lines from simulator points. No IBM credentials or hardware are needed.

The official Devpost overview and rules were read in the browser. They confirm November 8, 2026, 08:00 Eastern / 21:00 Beijing. The overview includes participant eligibility labels while the rules say registration is open to all; eligibility has not been assessed for the participant and is not claimed here.

## Resolved issues

The first static figure export encountered round-off in the zero-error Wilson lower bound. Endpoint clamping fixes nonnegative interval lengths. An early UI check ran before the evidence bundle finished; the loader now checks metadata availability. Direct Aer execution in Streamlit's macOS script thread caused a native process crash during real browser testing; live runs now use an isolated Python worker with captured failures and a timeout. Fresh execution and explicit cache reuse were then verified in the browser. No failed test was deleted to hide a failure.

## Remaining submission actions

The code and all text materials are ready. A demo video has not been recorded or uploaded. Devpost is not authenticated in the available browser; no Devpost project has been created or submitted. Participant details and final entry submission remain with the user. No external app hosting has been deployed; the Streamlit app runs locally.

## Repository publication

Created the public repository https://github.com/Tomhao10225101490/QuantumNoise-Lab with the already configured local GitHub credential. The initial push was rejected because the OAuth credential lacks workflow scope. The workflow was retained as docs/ci/verify.yml (inactive template), allowing code publication without broadening access. Local checks remain completed; no remote Actions success is claimed.
