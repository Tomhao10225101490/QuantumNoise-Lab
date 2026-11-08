"""Launch from the repository root: streamlit run app/main.py."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis.plotting import benefit_heatmap, comparison
from quantum.circuits import repetition_circuit
from quantum.noise_models import correlation, distribution
from quantum.simulator import Config
from quantum.worker import execute

st.set_page_config(page_title="QuantumNoise Lab", page_icon="◌", layout="wide")
st.markdown(
    """<style>
.block-container {max-width:1320px; padding-top:4.5rem;}
h1 {font-weight:650; letter-spacing:-.05em; font-size:3.3rem;}
h2 {letter-spacing:-.025em;}
[data-testid="stMetricValue"] {font-size:2rem;}
[data-testid="stSidebar"] {border-right:1px solid #dce4de;}
.lab-label {font-size:.75rem;letter-spacing:.16em;color:#087f72;font-weight:700;}
</style>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### ◌ QuantumNoise Lab")
    st.caption("QISKIT FALL FEST · 2026")
    page = st.radio(
        "Workspace",
        [
            "Overview",
            "Interactive Noise Lab",
            "Quantum Circuit Explorer",
            "Noise Comparison",
            "Research Findings",
        ],
    )
    st.divider()
    st.caption("ENGINE")
    st.write("Qiskit Aer Simulator")
    st.caption("Clifford circuits + Pauli channels\n\nNo real hardware was used.")
    st.caption(
        "X-error protection in the computational basis. This code does not correct arbitrary quantum errors."
    )


def evidence():
    path = ROOT / "results/processed/summary.csv"
    if (
        not path.exists()
        or not (ROOT / "results/processed/configuration.json").exists()
    ):
        st.warning("Evidence bundle missing. Run: python -m experiments.run_all")
        st.stop()
    return pd.read_csv(path)


def chart(fig):
    st.plotly_chart(fig, width="stretch")


def download(frame, name):
    st.download_button(
        "Download displayed data · CSV", frame.to_csv(index=False), name, "text/csv"
    )


st.markdown(
    '<div class="lab-label">QUANTUM ERROR CORRECTION / EXPERIMENTAL WORKSPACE</div>',
    unsafe_allow_html=True,
)

if page == "Overview":
    st.title("When does correction actually help?")
    st.markdown(
        "Three physical qubits. One logical bit. A controlled study of where repetition protects information—and where it fails."
    )
    summary = evidence()
    base = summary[(summary.experiment == "baseline") & (summary.input_state == 0)]
    sample = base[base.p == 0.1].set_index("model")
    a, b, c = st.columns(3)
    a.metric("Unencoded · p = 0.10", f"{sample.loc['raw', 'observed_error_rate']:.2%}")
    b.metric(
        "Encoded · independent noise",
        f"{sample.loc['encoded', 'observed_error_rate']:.2%}",
    )
    c.metric(
        "Observed error reduction",
        f"{1 - sample.loc['encoded', 'observed_error_rate'] / sample.loc['raw', 'observed_error_rate']:.1%}",
    )
    chart(comparison(base))
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Redundancy has a condition")
        st.latex(
            r"\alpha|0\rangle+\beta|1\rangle\ \longrightarrow\ \alpha|000\rangle+\beta|111\rangle"
        )
        st.write(
            "Two parity checks reveal a single X error without measuring the encoded amplitudes. Conditional X gates repair the indicated qubit. Two X errors imitate a different single error and lead to a logical failure."
        )
        st.latex(r"P_{L,\mathrm{iid}}=3p^2-2p^3")
        st.caption(
            "Experiments prepare |0⟩ and |1⟩. We measure output Z errors; we do not claim an arbitrary-state fidelity benchmark."
        )
    with right:
        st.subheader("What the evidence says")
        st.write(
            "Independent X noise is suppressed for 0 < p < 0.5 with ideal correction. Pair-correlated flips can erase that advantage while every physical qubit keeps the same error probability. Faulty syndrome reports add a cost even at p = 0."
        )
        config = json.loads((ROOT / "results/processed/configuration.json").read_text())
        st.caption(
            f"Source: {config['rows']} circuit runs · {config['total_shots']:,} total shots · 3 fixed seeds. Error bars: pointwise 95% Wilson intervals. Dotted lines: analytical theory; markers: Aer observations."
        )
    st.image(
        str(ROOT / "results/figures/baseline.png"),
        caption="Exported figure from the same CSV used above.",
    )

elif page == "Interactive Noise Lab":
    st.title("Run a controlled experiment")
    st.write(
        "Each new configuration executes two actual Qiskit circuits. Previously executed configurations may be reused with an explicit cache label."
    )
    with st.form("experiment"):
        a, b, c = st.columns(3)
        p = a.slider("Physical Error Probability", 0.0, 0.5, 0.1, 0.01)
        model = b.selectbox(
            "Noise Model", ["Independent bit flips", "Fixed-marginal correlated pairs"]
        )
        strength = c.slider("Correlation Strength", 0.0, 1.0, 0.5, 0.05)
        a, b, c = st.columns(3)
        state = a.selectbox("Initial State", [0, 1])
        shots = b.select_slider(
            "Number of Shots", options=[1024, 4096, 8192, 32768], value=8192
        )
        seed = c.number_input("Random Seed", 0, 2**32 - 1, 2026, 1)
        m = st.slider(
            "Syndrome report flip probability m (extension)", 0.0, 0.2, 0.0, 0.01
        )
        force = st.checkbox("Force fresh Aer execution even if cached")
        submitted = st.form_submit_button("Run Simulation", type="primary")
    if submitted:
        cfg = Config(
            p,
            strength if model.startswith("Fixed") else 0.0,
            m,
            state,
            shots,
            int(seed),
        )
        key = tuple(asdict(cfg).values())
        cache = st.session_state.setdefault("executed_cache", {})
        if key in cache and not force:
            rows, source = (
                cache[key],
                "CACHE HIT · previously executed Qiskit Aer result",
            )
        else:
            with st.spinner(
                "Executing encoding, noise, syndrome measurement and conditional recovery…"
            ):
                rows = execute(cfg)
            cache[key] = rows
            source = "FRESH EXECUTION · Qiskit Aer Simulator"
        st.session_state["last_result"] = (rows, source)
    if "last_result" in st.session_state:
        rows, source = st.session_state["last_result"]
        st.success(source)
        frame = pd.DataFrame(rows)
        cfg = rows[0]
        st.caption(
            f"Executed configuration: p={cfg['p']}, c={cfg['c']}, m={cfg['m']}, input |{cfg['state']}⟩, shots={cfg['shots']:,}, seed={cfg['seed']}. Change controls and press Run Simulation to update."
        )
        raw, encoded = rows
        a, b, c = st.columns(3)
        a.metric("No Encoding", f"{raw['observed_error_rate']:.3%}")
        b.metric("Repetition Code", f"{encoded['observed_error_rate']:.3%}")
        c.metric(
            "Reduction vs observed raw",
            f"{1 - encoded['observed_error_rate'] / raw['observed_error_rate']:.1%}"
            if raw["observed_errors"]
            else "Undefined · raw = 0",
        )
        for r in rows:
            st.write(
                f"**{r['model'].title()}** · theory {r['theoretical_error_rate']:.4%} · 95% Wilson CI [{r['ci_low']:.4%}, {r['ci_high']:.4%}] · {r['observed_errors']:,} errors / {r['shots']:,} shots"
            )
        st.caption(
            "Logical error here is the Z error on recovered q0, equivalent to the output of an ideal inverse encoder. It is distinct from complete codeword recovery."
        )
        st.write(
            f"Complete codeword recovery success: {encoded['codeword_recovery_success_rate']:.3%}"
        )
        counts = json.loads(encoded["syndrome_counts"])
        chart(
            go.Figure(
                go.Bar(x=list(counts), y=list(counts.values()), marker_color="#087f72")
            ).update_layout(
                title="Measured syndrome distribution · s1s0",
                xaxis_title="Syndrome report",
                yaxis_title="Shots",
                template="plotly_white",
            )
        )
        st.dataframe(
            frame[
                [
                    "model",
                    "observed_errors",
                    "shots",
                    "observed_error_rate",
                    "theoretical_error_rate",
                    "ci_low",
                    "ci_high",
                    "runtime",
                ]
            ],
            hide_index=True,
            width="stretch",
        )
        download(frame, "interactive_aer_result.csv")
    else:
        st.info(
            "Choose a configuration, then press Run Simulation. No simulation has been run in this session."
        )

elif page == "Quantum Circuit Explorer":
    st.title("Inspect the actual circuit")
    a, b, c = st.columns(3)
    p = a.slider("Circuit physical p", 0.0, 0.5, 0.1, 0.01)
    strength = b.slider("Circuit correlation c", 0.0, 1.0, 0.0, 0.05)
    m = c.slider("Circuit syndrome noise m", 0.0, 0.2, 0.0, 0.01)
    state = st.selectbox("Circuit input state", [0, 1])
    qc = repetition_circuit(p, strength, m, state)
    st.write(
        "**Encode → Pauli channel → parity extraction → conditional X recovery → data measurement.** The quantum_channel instruction contains the explicit joint error distribution below."
    )
    with st.spinner("Drawing Qiskit circuit…"):
        fig = qc.draw(output="mpl", fold=60)
        st.pyplot(fig, width="stretch")
        import matplotlib.pyplot as plt

        plt.close(fig)
    st.code(str(qc.draw(output="text", fold=105)), language=None)
    st.markdown(
        "**Syndrome convention:** s0 = q0 ⊕ q1; s1 = q1 ⊕ q2. Displayed bitstrings use s1s0."
    )
    st.dataframe(
        pd.DataFrame(
            {
                "Report s1s0": ["00", "01", "11", "10"],
                "Recovery": ["None", "X on q0", "X on q1", "X on q2"],
                "Single-error explanation": [
                    "No X error",
                    "q0 flipped",
                    "q1 flipped",
                    "q2 flipped",
                ],
            }
        ),
        hide_index=True,
    )
    events = pd.DataFrame(
        [
            {"Mask q2q1q0": format(mask, "03b"), "Probability": prob}
            for mask, prob in distribution(p, strength).items()
        ]
    )
    st.dataframe(events, hide_index=True)
    st.caption(
        f"Each data qubit has marginal X-error probability p={p:.3f}. Pairwise Pearson correlation = {correlation(p, strength):.4f} (convention 0 at p=0)."
    )
    st.download_button(
        "Download circuit text", str(qc.draw(output="text")), "repetition_circuit.txt"
    )

elif page == "Noise Comparison":
    st.title("Same physical noise. Different structure.")
    summary = evidence()
    correlated = summary[summary.experiment == "correlated"]
    chart(
        comparison(
            correlated[correlated.model == "encoded"],
            "c",
            "Joint errors change the outcome",
        )
    )
    chart(benefit_heatmap(correlated))
    st.latex(r"P(E=e)=(1-c)p^{|e|}(1-p)^{3-|e|}+c\,P_{\mathrm{pair}}(e)")
    st.write(
        "Pair channel: P(000)=1−3p/2; P(011)=P(101)=P(110)=p/2. Other events have zero probability. Legal ranges: 0≤p≤0.5, 0≤c≤1. This preserves each marginal p; c is a mixture weight, not a Pearson coefficient."
    )
    st.latex(r"P_L=(1-c)(3p^2-2p^3)+c\frac{3p}{2}")
    st.write(
        "At c=1, every nonzero event flips two qubits. The decoder mistakes it for one error on the remaining qubit. At p=0.5 the pairwise Pearson correlation is zero, yet the joint distribution is still dependent: pairwise correlation alone does not characterize this channel."
    )
    st.subheader("What faulty parity reports cost")
    noisy = summary[(summary.experiment == "break_even") & (summary.model == "encoded")]
    chart(comparison(noisy, "m", "Noisy syndrome vs ideal correction"))
    st.caption(
        "Only the two syndrome reports are noisy; each flips independently with probability m. Encoding, CNOTs, recovery gates and final measurement are ideal. Crossings are model-specific break-even points, not fault-tolerance thresholds."
    )
    st.write(
        "At m=0.10, measured benefit changes sign between p=0.10 and 0.15. Exact model enumeration predicts harm below p≈0.129190 and benefit for 0.129190<p<0.5. Sampling can leave points near a crossing unresolved."
    )
    with st.expander("Inspect benefit intervals and model-specific crossings"):
        benefit = pd.read_csv(ROOT / "results/processed/benefit.csv")
        st.dataframe(benefit, hide_index=True)
        st.caption(
            "Benefit = observed raw error − encoded error. Difference of two 97.5% Wilson intervals gives an approximately 95% pointwise Bonferroni interval. No across-grid confidence guarantee."
        )
        st.json(json.loads((ROOT / "results/processed/break_even.json").read_text()))
    with st.expander("Inspect measured data"):
        st.dataframe(summary, hide_index=True)
        download(summary, "summary.csv")

else:
    st.title("Findings, with boundaries")
    st.subheader("01 · Independent X errors are correctable")
    st.write(
        "Hypothesis: one X error is repaired, while two or three produce a logical failure. Exhaustive deterministic injection checks all eight patterns for both basis inputs. Monte Carlo sweeps compare to 3p²−2p³ across ten physical probabilities."
    )
    st.subheader("02 · Marginals do not determine protection")
    st.write(
        "Hypothesis: changing only the joint error structure can reverse the benefit. Our fixed-marginal pair mixture raises the ideal logical error from 3p²−2p³ to 1.5p as c reaches 1. All plotted markers are actual Aer outcomes; dotted curves are independently computed theory."
    )
    st.subheader("03 · Reading the syndrome has a cost")
    st.write(
        "Hypothesis: faulty reports can cause unnecessary recovery. With p=0, the output-q0 error floor is m(1−m). At nonzero p, exact enumeration of eight data patterns and four report patterns provides a separate prediction. The complete recovered-codeword success rate is separately recorded."
    )
    st.subheader("Scope and limitations")
    st.write(
        "One correction round; Pauli X storage channel; basis-state inputs; no phase-error protection, hardware calibration, leakage, coherent errors, or fault-tolerant syndrome circuits. We benchmark a decoded Z observable, not arbitrary quantum-state fidelity. Aer stabilizer simulation is exact for this Clifford/Pauli circuit family, followed by finite-shot sampling."
    )
    st.write(
        "95% Wilson intervals are pointwise uncertainty estimates, not simultaneous confidence bands. Repeated seed/configuration pairs across experiment families reuse the same pseudorandom stream and must not be pooled as independent replicates across families. Separate raw and encoded jobs are not paired trials."
    )
    st.subheader("Reproduce and audit")
    config = json.loads((ROOT / "results/processed/configuration.json").read_text())
    st.json(config)
    st.code(
        "python -m pytest -q\npython -m experiments.run_all\nstreamlit run app/main.py",
        language="bash",
    )
    st.download_button(
        "Download raw circuit-run CSV",
        (ROOT / "results/raw/experiments.csv").read_bytes(),
        "experiments.csv",
        "text/csv",
    )
