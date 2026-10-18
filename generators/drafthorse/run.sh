#!/usr/bin/env bash
# usage: generators/drafthorse/run.sh <corpus_dir> <out_dir>
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
python3 -m venv "$H/.venv" && "$H/.venv/bin/pip" -q install -r "$H/requirements.txt"
"$H/.venv/bin/python" "$H/gen.py" "$1" "$2"
