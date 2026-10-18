#!/usr/bin/env bash
# usage: generators/mustang/run.sh <corpus_dir> <out_dir>   (needs JDK 17+; uses the pinned Mustang-CLI jar)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"; R="$H/../.."
T="${EICM_TOOLS:-$R/.tools}"
[[ -f "$T/optional/Mustang-CLI-2.26.0.jar" ]] || bash "$R/validators/fetch_pinned.sh" --with-optional
mkdir -p "$H/build"; javac -d "$H/build" -cp "$T/optional/Mustang-CLI-2.26.0.jar" "$H/GenM.java"
java -cp "$T/optional/Mustang-CLI-2.26.0.jar:$H/build" GenM "$1/carts_net.json" "$2"
