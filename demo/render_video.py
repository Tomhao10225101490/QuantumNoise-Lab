"""Render an edited, narrated walkthrough from real captured UI and saved evidence."""

import json
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "demo"
FPS = 12
W, H = 1280, 720
BG = "#102d29"
WHITE = "#f4f6ef"
MUTED = "#b5cbc2"
ACCENT = "#7bdbb4"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def wrapped(draw, text, xy, width, size=30, fill=WHITE, bold=False, spacing=10):
    f = font(size, bold)
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textlength(candidate, font=f) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += size + spacing
    return y


def make_plots():
    data = pd.read_csv(ROOT / "results/processed/summary.csv")
    for experiment, group, name in [
        ("correlated", "c", "correlation"),
        ("break_even", "m", "cost"),
    ]:
        frame = data[(data.experiment == experiment) & (data.model == "encoded")]
        fig, ax = plt.subplots(figsize=(12, 4.5), dpi=120)
        colors = ["#087f72", "#c76c34", "#526477", "#973d5e", "#7c8036"]
        for color, (key, part) in zip(colors, frame.groupby(group), strict=True):
            part = part.sort_values("p")
            ax.errorbar(
                part.p,
                part.observed_error_rate,
                yerr=[
                    part.observed_error_rate - part.ci_low,
                    part.ci_high - part.observed_error_rate,
                ],
                fmt="o",
                markersize=4,
                capsize=2,
                color=color,
                label=f"{group}={key:g}: Aer",
            )
            ax.plot(part.p, part.theoretical_error_rate, ":", color=color)
        ax.plot(
            [0, 0.5],
            [0, 0.5],
            color="#333333",
            linewidth=1.2,
            label="Unencoded theory: p",
        )
        ax.set(
            xlabel="Physical X-error probability p",
            ylabel="Decoded output Z-error probability",
        )
        ax.grid(alpha=0.15)
        ax.legend(ncol=3, fontsize=10)
        fig.tight_layout()
        fig.savefig(D / f"assets/{name}.png")
        plt.close(fig)


def base(chapter):
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)
    draw.text((42, 20), "QUANTUMNOISE LAB", font=font(20, True), fill=ACCENT)
    draw.text(
        (810, 24), "QISKIT FALL FEST 2026  /  AER SIMULATOR", font=font(14), fill=MUTED
    )
    draw.line((42, 57, 1238, 57), fill="#34534b", width=1)
    draw.text((42, 75), f"EXPERIMENT {chapter + 1:02d} / 06", font=font(14), fill=MUTED)
    return im, draw


def screen_card(chapter, title, notes, capture):
    im, draw = base(chapter)
    y = wrapped(draw, title, (42, 120), 540, size=43, bold=True)
    y += 30
    for note in notes:
        y = wrapped(draw, note, (46, y), 510, size=24, fill=MUTED, spacing=8) + 22
    shot = Image.open(D / "captures" / capture).convert("RGB")
    shot = shot.crop((0, 44, shot.width, shot.height))
    shot = ImageOps.contain(shot, (585, 530))
    x = 650 + (585 - shot.width) // 2
    y = 86 + (530 - shot.height) // 2
    im.paste(shot, (x, y))
    draw.rectangle(
        (x - 1, y - 1, x + shot.width, y + shot.height), outline="#75968b", width=1
    )
    draw.text(
        (650, 621),
        "Actual application capture · edited walkthrough",
        font=font(13),
        fill=MUTED,
    )
    return im


def diagram_card():
    im, draw = base(1)
    draw.text(
        (42, 114), "Encode. Measure parity. Recover.", font=font(40, True), fill=WHITE
    )
    draw.text(
        (42, 170),
        "Actual Qiskit QuantumCircuit.draw() output · 3 data qubits + 2 ancillas",
        font=font(20),
        fill=MUTED,
    )
    diagram = Image.open(ROOT / "results/figures/circuit_ideal.png").convert("RGB")
    diagram = ImageOps.contain(diagram, (1196, 325))
    im.paste(diagram, ((W - diagram.width) // 2, 232))
    draw.text(
        (50, 545),
        "Syndrome s1s0:  00 → none     01 → X(q0)     11 → X(q1)     10 → X(q2)",
        font=font(24, True),
        fill=ACCENT,
    )
    draw.text(
        (50, 586),
        "Repairs one X error. Two X errors imitate the complementary single error.",
        font=font(23),
        fill=MUTED,
    )
    return im


def plot_card(chapter, title, name, footer):
    im, draw = base(chapter)
    draw.text((42, 111), title, font=font(36, True), fill=WHITE)
    plot = Image.open(D / f"assets/{name}.png").convert("RGB")
    plot = ImageOps.contain(plot, (1196, 435))
    im.paste(plot, ((W - plot.width) // 2, 174))
    draw.text((42, 612), footer, font=font(17), fill=MUTED)
    return im


def closing():
    im, draw = base(5)
    wrapped(
        draw,
        "Reproduce the result. Inspect the assumptions.",
        (48, 120),
        1150,
        48,
        bold=True,
    )
    draw.text((48, 286), "720 saved circuit runs", font=font(34, True), fill=ACCENT)
    draw.text(
        (48, 344),
        "5,898,240 shots · 3 seeds · 50 passing tests",
        font=font(29),
        fill=WHITE,
    )
    draw.text(
        (48, 415),
        "Raw counts, circuit diagrams, confidence intervals and a live lab.",
        font=font(25),
        fill=MUTED,
    )
    draw.text(
        (48, 483),
        "github.com/Tomhao10225101490/QuantumNoise-Lab",
        font=font(27, True),
        fill=WHITE,
    )
    draw.text(
        (48, 556),
        "Simulation only · X errors · basis-state Z benchmark · one correction round",
        font=font(21),
        fill=MUTED,
    )
    draw.text(
        (48, 598),
        "Edited actual screen captures + evidence figures · synthetic English narration",
        font=font(17),
        fill=MUTED,
    )
    return im


def caption(im, text):
    image = im.copy()
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 644, W, H), fill="#061916")
    wrapped(draw, text, (48, 654), 1184, size=23, fill=WHITE, spacing=5)
    return image


def main():
    make_plots()
    texts = json.loads((D / "narration.json").read_text())
    # Recreate local narration intermediates when they are absent (macOS).
    (D / "audio").mkdir(exist_ok=True)
    durations = []
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for i, text in enumerate(texts):
        wav_path = D / f"audio/{i:02}.wav"
        if not wav_path.exists():
            text_path = D / f"audio/{i:02}.txt"
            text_path.write_text(text)
            aiff_path = wav_path.with_suffix(".aiff")
            subprocess.run(
                [
                    "say",
                    "-v",
                    "Daniel",
                    "-r",
                    "165",
                    "-f",
                    str(text_path),
                    "-o",
                    str(aiff_path),
                ],
                check=True,
            )
            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-i",
                    str(aiff_path),
                    "-ar",
                    "48000",
                    "-ac",
                    "1",
                    str(wav_path),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        with wave.open(str(wav_path)) as wav:
            durations.append(wav.getnframes() / wav.getframerate())
    chapters = []
    cursor = 1.0
    # Add silence between chapters, with the script defining each narrated section.
    wavs = []
    for i, (_text, duration) in enumerate(zip(texts, durations, strict=True)):
        with wave.open(str(D / f"audio/{i:02}.wav")) as wav:
            wavs.append(wav.readframes(wav.getnframes()))
        chapters.append(
            {
                "index": i,
                "start": cursor,
                "duration": duration,
                "end": cursor + duration,
            }
        )
        cursor += duration + 2
    total = cursor + 1
    with wave.open(str(D / "output/narration.wav"), "wb") as out:
        out.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        out.writeframes(bytes(48000 * 2))
        for audio in wavs:
            out.writeframes(audio)
            out.writeframes(bytes(2 * 48000 * 2))
        out.writeframes(bytes(48000 * 2))
    cards = {
        "overview": screen_card(
            0,
            "When does correction actually help?",
            [
                "A controlled experiment with real Qiskit circuits.",
                "Independent errors, correlated pairs, and the cost of reading a syndrome.",
                "Simulator observations are separate from theory.",
            ],
            "01_overview.jpg",
        ),
        "circuit": diagram_card(),
        "controls": screen_card(
            2,
            "Run the actual circuit.",
            [
                "p = 0.10 · input |0> · 8,192 shots",
                "Fixed seed: 2026",
                "Press Run Simulation to execute Aer. Sliders alone do not create a result.",
            ],
            "04_controls.jpg",
        ),
        "fresh": screen_card(
            2,
            "A measured result.",
            [
                "Live single-seed run: 232 encoded errors / 8,192 shots.",
                "Observed encoded rate: 2.832%.",
                "This is a new Aer execution, with a visible confidence interval.",
            ],
            "05_fresh_result.jpg",
        ),
        "pooled": plot_card(
            2,
            "Three-seed evidence: 10.107% raw → 2.812% encoded",
            "baseline",
            "24,576 shots per model · 95% Wilson intervals · dashed curves: analytical theory",
        ),
        "cache": screen_card(
            2,
            "Cache reuse is explicit.",
            [
                "The displayed badge identifies a previously executed result.",
                "Force fresh execution is available.",
                "New parameters trigger a new Aer job.",
            ],
            "06_cached_result.jpg",
        ),
        "correlation": screen_card(
            3,
            "Hold physical noise fixed.",
            [
                "Each physical marginal remains p.",
                "The mixture weight c changes the joint distribution.",
                "At p=0.10 and c=1: 14.945% observed encoded error.",
            ],
            "07_correlation.jpg",
        ),
        "corrplot": plot_card(
            3,
            "Pair errors can reverse the benefit.",
            "correlation",
            "Dots: Aer observations ± 95% Wilson intervals · dotted curves: exact theory",
        ),
        "heatmap": screen_card(
            3,
            "Where correction helps.",
            [
                "Benefit = p − observed encoded error.",
                "Positive values indicate improvement against the known raw marginal.",
                "No claim of a universal threshold.",
            ],
            "08_heatmap.jpg",
        ),
        "cost": plot_card(
            4,
            "Syndrome reports also have a cost.",
            "cost",
            "Only report errors are added · encoding, CNOTs, recovery and final readout remain ideal",
        ),
        "limits": screen_card(
            4,
            "A model-specific crossing.",
            [
                "m = 0.10: observed sign change between p=0.10 and p=0.15.",
                "Exact model root: p ≈ 0.129190.",
                "Decoded Z error; no arbitrary-state fidelity or hardware claim.",
            ],
            "11_findings.jpg",
        ),
        "closing": closing(),
    }
    # Baseline export is the original plot generated by the experiment pipeline.
    subtitles = []
    for chapter, text in zip(chapters, texts, strict=True):
        words = text.split()
        chunks = []
        chunk = []
        for word in words:
            chunk.append(word)
            if len(" ".join(chunk)) >= 100 or (
                word.endswith((".", "?")) and len(chunk) >= 6
            ):
                chunks.append(" ".join(chunk))
                chunk = []
        if chunk:
            chunks.append(" ".join(chunk))
        consumed = 0
        for chunk in chunks:
            weight = len(chunk.split()) / len(words)
            start = chapter["start"] + consumed * chapter["duration"]
            end = start + weight * chapter["duration"]
            subtitles.append({"start": start, "end": end, "text": chunk})
            consumed += weight

    def srt_time(seconds):
        milliseconds = round(seconds * 1000)
        seconds, ms = divmod(milliseconds, 1000)
        minutes, s = divmod(seconds, 60)
        hours, m = divmod(minutes, 60)
        return f"{hours:02}:{m:02}:{s:02},{ms:03}"

    (D / "output/QuantumNoise-Lab.en.srt").write_text(
        "\n\n".join(
            f"{i + 1}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}"
            for i, c in enumerate(subtitles)
        )
        + "\n"
    )
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output = D / "output/QuantumNoise-Lab-demo.mp4"
    command = [
        ffmpeg,
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        "1280x720",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-i",
        str(D / "output/narration.wav"),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        "-shortest",
        str(output),
    ]
    cache = {}
    with (D / "output/render.log").open("w") as log:
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=log, stderr=log
        )
        for frame in range(round(total * FPS)):
            t = frame / FPS
            chapter = next(
                (c for c in reversed(chapters) if t >= c["start"]), chapters[0]
            )
            index = chapter["index"]
            local = t - chapter["start"]
            fraction = max(0, local / chapter["duration"])
            if index == 0:
                key = "overview"
            elif index == 1:
                key = "circuit"
            elif index == 2:
                key = (
                    "controls"
                    if fraction < 0.22
                    else "fresh"
                    if fraction < 0.55
                    else "pooled"
                    if fraction < 0.82
                    else "cache"
                )
            elif index == 3:
                key = (
                    "correlation"
                    if fraction < 0.3
                    else "corrplot"
                    if fraction < 0.78
                    else "heatmap"
                )
            elif index == 4:
                key = "cost" if fraction < 0.58 else "limits"
            else:
                key = "closing"
            line = next(
                (c["text"] for c in subtitles if c["start"] <= t < c["end"]), ""
            )
            item = (key, line)
            if item not in cache:
                cache[item] = caption(cards[key], line).tobytes()
            process.stdin.write(cache[item])
        process.stdin.close()
        if process.wait():
            raise RuntimeError("ffmpeg failed; inspect render.log")
    metadata = {
        "duration_seconds": total,
        "resolution": [1280, 720],
        "fps": FPS,
        "narration": "macOS Daniel synthetic voice, 165 wpm",
        "chapters": chapters,
        "format": "Edited actual application screen captures with held frames, Qiskit circuit export and measured-evidence plots; not an uncut continuous recording.",
        "caption_alignment": "Script-based proportional timing; English captions are approximate at sentence/chunk level.",
        "hardware": False,
        "file_bytes": output.stat().st_size,
    }
    (D / "output/metadata.json").write_text(json.dumps(metadata, indent=2))
    cards["overview"].save(D / "output/poster.png")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
