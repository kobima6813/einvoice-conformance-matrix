#!/usr/bin/env bash
# usage: generators/speedata/run.sh <corpus_dir> <out_dir>   (needs the Go version in go.mod)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
(cd "$H" && go run . "$1/carts_net.json" "$2")
