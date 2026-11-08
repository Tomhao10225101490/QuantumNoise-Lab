# Three-minute demo script

## 0:00–0:20 — The question (Overview)
“Quantum error correction is supposed to protect quantum information. But when does its extra machinery actually help? QuantumNoise Lab tests that question using a three-qubit repetition code, real Qiskit circuits, and reproducible simulator evidence.”

## 0:20–0:50 — The code (Circuit Explorer)
“We encode one qubit across three data qubits. Two ancillas measure parity checks, and the measured syndrome controls an X correction. One bit flip is correctable. Two flips imitate a single error on the remaining qubit, so the decoder makes the wrong choice. This code protects against X errors; it does not correct arbitrary quantum noise.”

## 0:50–1:30 — Run the experiment (Interactive Noise Lab)
“Here the physical error probability is ten percent. I choose independent noise, a basis-state input, a fixed seed and 8,192 shots, then press Run Simulation. This executes Aer; moving a slider alone does not generate a result. We display observed errors, the theoretical prediction and a confidence interval. Across the saved three-seed experiment, the raw error is about ten percent and the encoded error is about 2.8 percent. A repeated configuration is explicitly labeled as cached, and I can force a fresh run.”

## 1:30–2:10 — Change structure, not strength (Noise Comparison)
“Now we keep each physical qubit's error probability unchanged and introduce pair events. The correlation control mixes independent noise with a channel that flips pairs together. At full pair-mixture strength, the encoded error reaches about fifteen percent—worse than leaving the information unencoded. The measured points follow the separately labeled theory. The heatmap shows positive and negative correction benefit over the full parameter sweep.”

## 2:10–2:40 — Cost and limits (Noise Comparison / Findings)
“Correction also depends on reading the syndrome correctly. Our extension flips each parity report with a controlled probability. At a ten-percent report-error rate, the measured benefit changes sign between physical error probabilities of ten and fifteen percent. This is a break-even region for one simplified model, not a universal threshold. We measure decoded Z errors on basis inputs, not arbitrary-state fidelity, and use Aer simulation rather than real hardware.”

## 2:40–3:00 — Value (Overview)
“The deliverable includes more than five million actual simulator shots, raw counts, fixed seeds, automated tests, circuit images and an interactive lab. The lesson is simple: whether correction helps depends on the structure of the errors and the cost of extracting information about them. The repository lets anyone reproduce and challenge that result.”

## Before recording
Start the app, verify the evidence bundle loads, and keep the circuit page ready. Avoid waiting for a full sweep during the demo. A single live configuration is sufficient to demonstrate real execution. The spoken results above are rounded from the saved 24,576-shot estimates; live one-seed results naturally fluctuate. Record and upload the actual video separately; this script is not a completed demo video.
