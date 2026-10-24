#!/usr/bin/env bash
# Reproduce results/fr/fr_results.json. usage: scenarios/fr/run_fr.sh [workdir]   (Python 3.9+, PHP 8.1+, composer, Java 17+)
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; R="$H/../.."; W="${1:-$R/work_fr}"; rm -rf "$W"; mkdir -p "$W"
[[ -n "${EICM_TOOLS:-}" ]] || bash "$R/validators/fetch_pinned.sh"
python3 -m venv "$W/venv" && "$W/venv/bin/pip" -q install -r "$R/generators/facturx/requirements.txt"
"$W/venv/bin/python" "$H/gen_drafthorse.py" "$H/scenarios.json" "$W/out"
for v in 1.0.132 1.0.133; do
  mkdir -p "$W/hk$v"; echo "{ \"require\": { \"horstoeko/zugferd\": \"$v\" } }" > "$W/hk$v/composer.json"
  (cd "$W/hk$v" && composer install -q --no-interaction)
  php "$H/gen_horstoeko.php" "$W/hk$v/vendor/autoload.php" "$H/scenarios.json" "$W/out" "$v"
done
"$H/validate.sh" "$W/out"
mkdir -p "$R/results/fr"; python3 - "$W/out/fr_results.json" "$R/results/fr/fr_results.json" <<'PY'
import json,sys,os
rows=json.load(open(sys.argv[1]))
for r in rows: r.pop('file',None)
json.dump(rows,open(sys.argv[2],'w'),indent=1,ensure_ascii=False)
PY
