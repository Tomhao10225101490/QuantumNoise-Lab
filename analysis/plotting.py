import plotly.graph_objects as go

COLORS = ["#087f72", "#c76c34", "#526477", "#973d5e", "#7c8036"]


def comparison(frame, group="model", title="Theory and Qiskit Aer simulation"):
    fig = go.Figure()
    for i, (name, data) in enumerate(frame.groupby(group)):
        data = data.sort_values("p")
        color = COLORS[i % len(COLORS)]
        fig.add_trace(
            go.Scatter(
                x=data.p,
                y=data.observed_error_rate,
                mode="markers",
                name=f"{name} · Aer",
                marker={"color": color, "size": 7},
                error_y={
                    "type": "data",
                    "array": data.ci_high - data.observed_error_rate,
                    "arrayminus": data.observed_error_rate - data.ci_low,
                    "symmetric": False,
                },
                customdata=data[["shots", "observed_errors"]],
                hovertemplate="p=%{x:.3f}<br>error=%{y:.4f}<br>shots=%{customdata[0]}<br>errors=%{customdata[1]}<extra>%{fullData.name}</extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data.p,
                y=data.theoretical_error_rate,
                mode="lines",
                line={"color": color, "dash": "dot"},
                name=f"{name} · theory",
            )
        )
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=460,
        xaxis_title="Marginal physical X-error probability p",
        yaxis_title="Output Z-error probability",
        legend={"orientation": "h", "y": -0.25},
        margin={"l": 40, "r": 20, "t": 60, "b": 100},
        font={"family": "Arial", "color": "#182d2b"},
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def benefit_heatmap(frame):
    data = frame[frame.model == "encoded"].copy()
    data["benefit"] = data.p - data.observed_error_rate
    pivot = data.pivot(index="c", columns="p", values="benefit")
    fig = go.Figure(
        go.Heatmap(
            x=pivot.columns,
            y=pivot.index,
            z=pivot.values,
            colorscale="BrBG",
            zmid=0,
            colorbar_title="p − logical",
            hovertemplate="p=%{x}<br>c=%{y}<br>benefit=%{z:.4f}<extra>Aer estimate</extra>",
        )
    )
    fig.update_layout(
        title="Correction benefit · fixed marginal noise",
        xaxis_title="Physical p",
        yaxis_title="Pair-mixture strength c",
        template="plotly_white",
        height=440,
    )
    return fig
