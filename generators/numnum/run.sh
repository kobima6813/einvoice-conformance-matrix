#!/usr/bin/env bash
# usage: generators/numnum/run.sh <corpus_dir> <out_dir>   (needs PHP 8.1+, composer, Python 3.9+)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
(cd "$H" && composer install -q --no-interaction)
mkdir -p "$2"; python3 "$H/prep.py" "$1" "$2/.ref.json"; php "$H/gen.php" "$2/.ref.json" "$2"; rm -f "$2/.ref.json"
