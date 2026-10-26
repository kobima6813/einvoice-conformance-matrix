#!/usr/bin/env bash
# usage: generators/e-invoice-eu/run.sh <corpus_dir> <out_dir>   (needs Node 18+; exact versions via package-lock.json)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
(cd "$H" && npm ci --ignore-scripts --no-audit --no-fund -q)
node "$H/gen.mjs" "$1/ref_en16931_rounding.json" "$2"
