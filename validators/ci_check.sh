#!/usr/bin/env bash
# usage: ci_check.sh <invoice_dir> [expected.json] [fail-on]
#   expected.json: optional {"<invoice file name without .xml>" or "<id>": "<charged amount>"}
#   fail-on: 'any' (default), 'none' (report only) or a comma list of rule ids / DUE-NE-CHARGED / ARITH-EXACT / XSD
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="$(mktemp -d)"
python3 "$HERE/../scripts/unpack_invoices.py" "$D" "$1" > /dev/null
bash "$HERE/run_oracle.sh" "$D"
python3 "$HERE/ci_report.py" "$D/out/oracle_rows.json" "$D/inputs" "${2:-}" "${3:-any}"
