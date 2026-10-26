#!/usr/bin/env bash
# usage: generators/attestwire/run.sh <corpus_dir> <out_dir>   (needs Node 18+ and npm; exact version via package-lock.json)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
(cd "$H" && npm ci --ignore-scripts --no-audit --no-fund -q)
node "$H/gen.mjs" "$1/carts_net.json" "$2"
