#!/usr/bin/env bash
# Reproduce results/matrix.{csv,md} from the shipped invoices.
# usage: scripts/run_matrix.sh [workdir]   (default: ./work; needs Java 17+ and Python 3.9+)
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
W="${1:-$R/work}"; rm -rf "$W"; mkdir -p "$W"
bash "$R/validators/fetch_pinned.sh"
python3 "$R/scripts/unpack_invoices.py" "$W"
bash "$R/validators/run_oracle.sh" "$W"
python3 "$R/scripts/matrix.py" "$W/out/oracle_rows.json" "$W/inputs" "$R/corpus/expected_paid.json" "$W/matrix" "$R/invoices/platform_order_totals.json" > /dev/null
python3 "$R/scripts/check_headlines.py" "$W/matrix.csv" "$R/results/matrix.csv"
