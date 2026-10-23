#!/usr/bin/env bash
# usage: generators/josemmo/run.sh <corpus_dir> <out_dir>   (needs PHP 8.1+ and composer)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
(cd "$H" && composer install -q --no-interaction)
for c in default round2; do php "$H/gen.php" "$1/carts_net.json" "$2" "$c"; done
