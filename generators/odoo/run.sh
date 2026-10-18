#!/usr/bin/env bash
# Regenerate the Odoo outputs (odoo19-*). Needs PostgreSQL, Python 3.10+ and an Odoo 19.0 Community
# checkout (outputs were produced at commit 53ec5874). Not run in CI.
# usage: ODOO=/path/to/odoo DB=ein generators/odoo/run.sh <corpus_dir> <out_dir>
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; C="$(cd "$1" && pwd)"; mkdir -p "$2"; OUT="$(cd "$2" && pwd)"
: "${ODOO:?set ODOO to an Odoo 19.0 checkout}"; DB="${DB:-ein}"
"$ODOO/odoo-bin" -d "$DB" -i account_edi_ubl_cii,l10n_de --without-demo=all --stop-after-init
for R in round_per_line round_globally; do
  N=300 ROUND=$R OUT="$OUT" CARTS="$C/carts_b2b.json,$C/carts_b2c.json" "$ODOO/odoo-bin" shell -d "$DB" --no-http < "$H/gen.py"
done
