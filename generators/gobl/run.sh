#!/usr/bin/env bash
# usage: generators/gobl/run.sh <corpus_dir> <out_dir>   (needs Go per go.mod, Python 3.9+)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$2"; python3 "$H/prep.py" "$1" "$2/.carts.json"; (cd "$H" && go run . "$2/.carts.json" "$2"); rm -f "$2/.carts.json"
