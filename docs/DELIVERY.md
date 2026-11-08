# Delivery

Public source and evidence: https://github.com/Tomhao10225101490/QuantumNoise-Lab

The source/evidence commit was successfully pushed to main on November 8, 2026. The local working copy is in QuantumNoise-Lab. Run ./run.sh from that directory, or activate .venv and run python -m streamlit run app/main.py. The verified local preview is http://127.0.0.1:8501.

Completed: real five-qubit Qiskit circuits and syndrome-conditioned recovery, independent and fixed-marginal pair noise, syndrome-report-cost extension, 720 saved circuit runs / 5,898,240 shots, CSV/JSON evidence, five interactive figure exports, circuit images, five application views, 50 passing tests, compilation, Ruff, and real browser checks. No IBM hardware was used.

At p=0.10: observed unencoded error 10.107%, independent encoded error 2.812%, fully pair-mixture encoded error 14.945%. Each saved estimate pools three seeds and 24,576 shots. Full intervals, model assumptions and crossings are documented in FINDINGS.md.

Submission material: DEVPOST_SUBMISSION.md and DEMO_SCRIPT.md. The official deadline is November 8, 2026, 21:00 Asia/Shanghai / 08:00 Eastern Standard Time. Verified official source: https://qiskitatvt.devpost.com/rules.

Remaining: participant Devpost login and final submission; actual demo-video recording/upload. The app has not been publicly hosted. CI is supplied as an inactive template in docs/ci because the existing credential lacks workflow scope. No remote CI success is claimed.
