#!/usr/bin/env bash
# usage: validate.sh <out_dir>   (needs validators/fetch_pinned.sh tools in $EICM_TOOLS, Java 17+, python3 with lxml)
# Runs: Factur-X 1.09.2 XSD (per profile), CEN EN16931 CII XSLT, Factur-X EXTENDED schematron (EXTENDED only),
# KoSIT 1.6.3 (XRechnung 3.0.2 configuration, which also carries an EN16931 CII scenario), then fr_checks.py.
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; T="${EICM_TOOLS:-$H/../../.tools}"; T="$(cd "$T" && pwd)"; O="$(cd "$1" && pwd)"
CP="$T/lib/Saxon-HE-12.10.jar:$T/lib/xmlresolver-5.3.3.jar:$T/lib/xmlresolver-5.3.3-data.jar"
SAX="java -Xmx2g -cp $CP net.sf.saxon.Transform"
for P in EN16931 EXTENDED; do
  mkdir -p "$O/val/cen_$P" "$O/val/kosit_$P"
  $SAX -s:"$O/$P" -xsl:"$T/cen/EN16931-CII-validation.xslt" -o:"$O/val/cen_$P" 2>>"$O/val/saxon.log" || true
  java -Xmx2g -jar "$T/validator-1.6.3-standalone.jar" -s "$T/xr/scenarios.xml" -r "$T/xr" -o "$O/val/kosit_$P" "$O/$P"/*.xml >> "$O/val/kosit_stdout.txt" 2>&1 || true
done
mkdir -p "$O/val/fx_EXTENDED"
(cd "$T/optional/facturx/EXTENDED/2xslt" && $SAX -s:"$O/EXTENDED" -xsl:FACTUR-X_EXTENDED.xslt -o:"$O/val/fx_EXTENDED" 2>>"$O/val/saxon.log" || true)
python3 "$H/fr_checks.py" "$O" "$T"
