#!/usr/bin/env bash
# Second validator: phive-rules 4.6.3 (XRechnung 3.0.2 for XRechnung documents, EN 16931 1.3.16 CII/UBL otherwise). usage: run_phive.sh <workdir>  -> <workdir>/out/phive.jsonl
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
(cd "$H" && mvn -q -B compile dependency:build-classpath -Dmdep.outputFile=cp.txt)
CP="$H/target/classes:$(cat "$H/cp.txt")"; : > "$1/out/phive.jsonl"
for k in cii ubl; do [[ -d "$1/inputs/$k" ]] || continue
  java -Xmx3g -cp "$CP" PhiveRun "$1/inputs/$k" "$1/out/phive_$k.jsonl"; cat "$1/out/phive_$k.jsonl" >> "$1/out/phive.jsonl"; done
