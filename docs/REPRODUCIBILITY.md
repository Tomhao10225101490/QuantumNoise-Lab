# Reproducibility notes

Run commands from the repository root. Tested environment: macOS arm64, Python 3.12.16, Qiskit 2.6.2, Qiskit Aer 0.18.2. The exact dependency set is locked in requirements.txt. Fresh installs use Python's standard venv and pip; the development environment was bootstrapped with uv.

1. Install requirements in a clean Python 3.12 environment.
2. Run `python -m experiments.run_all` to execute every circuit and regenerate raw CSV, pooled CSV, configuration JSON, figures and circuit images.
3. Run `python -m analysis.report` to regenerate benefit intervals, break-even JSON and the findings document.
4. Run `python -m pytest -q` and the compilation and Ruff commands in README.
5. Launch `python -m streamlit run app/main.py`.

No unrecorded NumPy sampling is used. Each job is an Aer stabilizer simulation with an explicit seed and exactly 8,192 shots. All gates are Clifford, all storage/report channels are stochastic Pauli channels, and recovery uses measured classical control. This backend choice is exact for the model and does not introduce a density-matrix approximation.

Raw fields include p, c, m, state/input_state, shots, seed, model, errors, empirical and exact rates, absolute discrepancy, Wilson endpoints, runtime in seconds, complete-codeword success, full output counts, syndrome counts, engine and versions. Bitstrings are `out2out1out0 s1s0` for encoded circuits. The logical output is out0; syndrome strings use s1 as the most significant bit.

Pooling sums errors and shots within each experiment/configuration/model. It does not average interval endpoints. Seeds 2026, 1701 and 31415 are treated as independent pseudorandom streams within a configuration. Configurations repeated across experiment families have identical seed streams and are not additional independent observations. Raw references at different c or m may likewise reuse the same raw-job seed: do not combine them as extra evidence.

Plotly exports and the application use the same pooled CSV, with analytical lines separately marked. The baseline PNG also reads this dataframe. CSV hashes in configuration.json cover the two primary data files; benefit.csv is a derived report. Expected reproducibility means identical counts under the tested software/backend settings; elapsed times, timestamps, generated file bytes and cross-version PRNG behavior are not guaranteed identical.

A 95% Wilson score interval is used for each binomial error rate, including zero-count endpoints. Benefit intervals subtract two 97.5% Wilson intervals, using a Bonferroni construction for approximately 95% pointwise coverage. No familywise confidence statement over the entire sweep is made. Observed crossing brackets use sign changes in estimates and are not confidence intervals for a threshold. The exact root of the specified analytical channel is separately labeled.

The noisy-syndrome extension evaluates decoded-q0 Z error, not an arbitrary-state logical-channel fidelity. No gate-depolarization model or real-device claim is included. Final data readout is ideal.

The original run finished successfully after fixing a floating-point endpoint issue in static error bars. A premature UI test while the evidence bundle was still being generated found missing metadata; the bundle guard was corrected and the complete suite was rerun. Results are not fabricated to avoid either failure.

Browser testing also exposed a native process crash when Aer was first called directly from a Streamlit script thread on this macOS environment. Live simulations now execute in a separate Python process through quantum.worker, with a timeout and captured errors; the circuit implementation is shared with batch experiments. Browser checks subsequently verified fresh execution and explicit cache reuse.
