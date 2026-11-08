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

The adjusted source/evidence commit was successfully pushed to main. Delivery is recorded in docs/DELIVERY.md. Core implementation, evidence and submission materials are complete; Devpost submission and video remain outstanding as explicitly listed.

## Demo and Devpost follow-up

Produced a 159.81-second 720p H.264/AAC edited screen-capture walkthrough, English synthesized narration and captions. FFmpeg decoded the entire video without errors; eight representative frames were visually checked. The existing Devpost draft was populated in the authenticated local Chrome session (project ID 1288205; slug quantumnoise-lab). Cloudflare verification was completed by the user. Media and final legal acceptance/submission are being completed separately; this note does not claim the entry is submitted.

The user completed YouTube channel creation/terms acceptance. The demo was uploaded and saved as unlisted at https://youtu.be/pw2w1IeWuGE. Devpost now shows DRAFT 3/4 steps done, with the complete story, Qiskit tag, code link, thumbnail, four captioned evidence images and the hosted video URL saved. The final terms checkbox remains unchecked and final competition submission is reserved for the participant. GitHub Release asset size/hash verification completed.

Final preview verified: the hosted YouTube video played inside the Devpost project page with audio and the actual circuit footage visible. The draft is ready at 3/4 steps; only participant acceptance of Official Rules/Devpost Terms and the final Submit project action remain.

## Final submission verified

2026-11-08T14:01:46.444401+08:00: The participant completed the terms checkbox and Submit project action. The browser then displayed the exact confirmation "Project submitted! Continue to edit your project until the hackathon deadline: November 08, 2026 at 08:00am EST." and a SUBMITTED TO section for Qiskit Fall Fest at Virginia Tech. Project URL: https://devpost.com/software/quantumnoise-lab. The demo, public repository and competition submission are now complete.
