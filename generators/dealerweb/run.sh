#!/usr/bin/env bash
# usage: generators/dealerweb/run.sh <corpus_dir> <out_dir>   (needs PHP 8.1+ and composer)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
(cd "$H" && composer install -q --no-interaction)
php "$H/gen.php" "$1/carts_net.json" "$2"
