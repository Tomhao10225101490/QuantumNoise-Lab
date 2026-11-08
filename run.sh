#!/bin/sh
set -eu
cd "$(dirname "$0")"
exec .venv/bin/python -m streamlit run app/main.py --browser.gatherUsageStats false
