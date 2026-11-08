# Measured findings



Generated from results/processed/summary.csv. All rates below are Aer observations; analytical predictions are identified separately.



At p=0.10 and input |0>, unencoded error is 0.10107; encoded independent error is 0.02812. Each estimate pools 24,576 shots across seeds 2026, 1701 and 31415.



At p=0.10, c=0.00: encoded error 0.02812, 95% Wilson [0.02612, 0.03026]; exact theory 0.02800.

At p=0.10, c=0.25: encoded error 0.05754, 95% Wilson [0.05469, 0.06052]; exact theory 0.05850.

At p=0.10, c=0.50: encoded error 0.08740, 95% Wilson [0.08394, 0.09100]; exact theory 0.08900.

At p=0.10, c=0.75: encoded error 0.11890, 95% Wilson [0.11491, 0.12300]; exact theory 0.11950.

At p=0.10, c=1.00: encoded error 0.14945, 95% Wilson [0.14505, 0.15397]; exact theory 0.15000.



## Syndrome-cost crossings



Only syndrome reports are noisy. The following low-p roots are analytical enumeration predictions, not universal thresholds. Observed sign-change brackets are saved in break_even.json; benefit.csv distinguishes supported benefit/harm from unresolved uncertainty.



m=0.01: theory predicts benefit for 0.010206 < p < 0.5; below the lower crossing the model predicts harm.

m=0.03: theory predicts benefit for 0.031980 < p < 0.5; below the lower crossing the model predicts harm.

m=0.05: theory predicts benefit for 0.055903 < p < 0.5; below the lower crossing the model predicts harm.

m=0.10: theory predicts benefit for 0.129190 < p < 0.5; below the lower crossing the model predicts harm.



## Limits



Decoded-q0 Z error differs from whole-codeword recovery with faulty reports. No IBM hardware, arbitrary-state fidelity, phase protection, or fault-tolerant threshold claim. Same seed/configuration repetitions across experiment families are duplicated evidence and must not be pooled as independent trials. At p=0.5 the pair-mixture channel can have zero pairwise correlation while retaining higher-order dependence.
