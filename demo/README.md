# Narrated demo

`output/QuantumNoise-Lab-demo.mp4` is an approximately 2 minute 40 second, 1280×720 H.264/AAC demonstration. English captions are burned into the video; a separate SRT is included. Narration uses the macOS Daniel system voice and is explicitly disclosed as synthetic.

This is an edited walkthrough using actual application screen captures, a real Qiskit circuit export, and figures generated from the saved Aer experiment CSV. Captures are held to match narration; this is not an uncut continuous recording. It shows an actual fresh seed-2026 run (232 encoded errors / 8,192 shots), distinguishes that result from the pooled 24,576-shot evidence, and shows explicit cache reuse. No result was fabricated for the video.

`render_video.py` assembles the video. The narrated script is in `narration.json`; source application captures are in `captures/`. Figure overlays read the primary summary CSV. Subtitle timing is approximated from script chunks within each narrated chapter. Private login screens and unrelated browser tabs are not included in the video.

The FFmpeg binary is supplied by imageio-ffmpeg 0.8.1, installed from PyPI. Install `requirements-video.txt` in the project environment in addition to the main requirements before rendering. This optional dependency is not needed to run the quantum lab.

The complete file passed FFmpeg decoding with no reported errors. Sample frames were extracted and visually inspected for the circuit diagram, live results, correlation comparison, correction-cost graph and closing evidence card.
