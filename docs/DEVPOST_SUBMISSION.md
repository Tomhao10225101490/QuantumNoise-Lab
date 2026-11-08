# Project Name
QuantumNoise Lab

## Elevator Pitch
When does quantum error correction actually help? A hands-on Qiskit lab shows how independent noise, correlated pairs and unreliable syndrome reports change the answer—even at the same physical error rate.

## Inspiration
The three-qubit repetition code is often introduced as a clean success story: encode, measure parity, correct one error. We wanted to turn that story into a testable question. What assumptions make the protection work, and how quickly does the benefit disappear when those assumptions change?

## What It Does
QuantumNoise Lab lets visitors run real Qiskit Aer circuits, inspect two measured syndromes and conditional recovery, compare observed errors with exact predictions, and explore confidence intervals. Five views connect a simple overview to a live experiment, circuit explorer, noise comparison and research findings.

Its controlled comparison holds every data qubit's marginal X-error probability fixed while mixing independent noise with explicitly defined pair events. This isolates the joint error structure instead of accidentally increasing the physical noise when adjusting “correlation.” A second extension introduces faulty parity reports and identifies model-specific break-even regions.

## How We Built It
We built a three-data-qubit code with two ancillas. Two CNOTs encode the input. A three-qubit Pauli channel injects data errors. Four CNOTs extract adjacent parity checks. Qiskit `if_test` blocks execute syndrome-conditioned X corrections before final measurement. Aer stabilizer simulation executes the actual circuits; this is an exact simulation method for this Clifford/Pauli model, followed by finite-shot sampling.

The evidence bundle contains 720 circuit runs and 5,898,240 shots. Each configuration uses three fixed seeds, with 8,192 shots per circuit per seed. Python modules separate the circuit model, simulator, statistics, experiment scripts and Streamlit interface. Plotly displays measured points with Wilson intervals and separately labeled analytical curves. CSV counts, configuration JSON, circuit images and offline plots are included.

## Challenges We Ran Into
Qiskit displays bitstrings in a different order from the physical-qubit labels used in many explanations. We made the parity convention explicit and tested all eight error masks for both basis inputs. Another challenge was defining a correlated channel without changing marginal error rates; an explicit pair-event mixture makes that comparison auditable.

Faulty syndrome reports also expose a measurement subtlety: correct output on the decoded first qubit does not guarantee that the entire block returned to the codespace. We record those metrics separately and state the observable being benchmarked. During validation, we fixed a floating-point confidence-interval endpoint issue and guarded against opening an incomplete evidence bundle.

## Accomplishments
At p=0.10, our actual simulator estimates are 10.107% unencoded error and 2.812% encoded error under independent noise, close to the 2.800% theoretical prediction. With the same physical marginals and fully pair-mixture noise, the encoded estimate rises to 14.945%, close to the 15.000% prediction. The code can make the outcome worse even though every individual physical qubit has the same error rate.

For syndrome report error m=0.10, the observed correction-benefit sign changes between p=0.10 and 0.15. Exact enumeration predicts a lower crossing near 0.129190. We describe this as a crossing for our simplified model, not a general fault-tolerance threshold.

## What We Learned
Physical error rates alone are insufficient to predict correction performance. The error distribution and the reliability of the correction process matter. We also learned to separate analytical predictions, simulator observations and statistical uncertainty, and to distinguish decoded-output error from complete codeword recovery.

## What's Next
Future work could add calibrated device noise, phase-error codes, multiple correction rounds, arbitrary-state process benchmarks and hardware runs. These are proposed extensions; they are not completed features of this submission.

## Built With
Python, Qiskit, Qiskit Aer, NumPy, Pandas, SciPy, Plotly, Matplotlib, Streamlit, pytest, Ruff. Implemented with Codex assistance during the event. Standard QEC concepts and official Qiskit API references are credited in the repository.

## Demo Instructions
Install requirements and run `python -m streamlit run app/main.py` from the repository root. Start on Overview, then run p=0.10, independent noise, input 0 and 8,192 shots in Interactive Noise Lab. Switch to the fixed-marginal pair model and set c=1, then press Run Simulation again. Inspect the parity-check circuit and compare the five measured correlation curves. In Noise Comparison, show the correction-benefit heatmap and the noisy-syndrome extension. Download the counts to audit a result.

Run `python -m experiments.run_all` followed by `python -m analysis.report` to regenerate the evidence bundle. Run `python -m pytest -q` for automated verification. No IBM Quantum account or API key is required. All completed experiments use Qiskit Aer Simulator; none ran on real IBM hardware.

## Code
https://github.com/Tomhao10225101490/QuantumNoise-Lab
