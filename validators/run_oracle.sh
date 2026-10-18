#!/usr/bin/env bash
# usage: run_oracle.sh <workdir>
#   <workdir>/inputs/{cii,ubl}/*.xml and <workdir>/inputs/index.json  ->  <workdir>/out/oracle_rows.json
# Runs KoSIT 1.6.3 (XRechnung 3.0.2 configuration), CEN EN16931 XSLT and Peppol BIS 3.0.20 schematron,
# then the exact-arithmetic checks in oracle.py. Requires validators/fetch_pinned.sh to have run.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="${EICM_TOOLS:-$HERE/../.tools}"; T="$(cd "$T" && pwd)"
cd "$1"
CP="$T/lib/Saxon-HE-12.10.jar:$T/lib/xmlresolver-5.3.3.jar:$T/lib/xmlresolver-5.3.3-data.jar"
SAX="java -Xmx2g -cp $CP net.sf.saxon.Transform"
mkdir -p out/kosit out/peppol_cii out/peppol_ubl out/cen_cii out/cen_ubl
shopt -s nullglob
files=(inputs/cii/*.xml inputs/ubl/*.xml)
# KoSIT in chunks (keeps the command line short for large corpora)
for ((i=0; i<${#files[@]}; i+=1000)); do
  java -Xmx3g -jar "$T/validator-1.6.3-standalone.jar" -s "$T/xr/scenarios.xml" -r "$T/xr" -o out/kosit \
    "${files[@]:i:1000}" >> out/kosit_stdout.txt 2>&1 || true
done
for k in cii ubl; do
  set -- inputs/$k/*.xml
  if [[ $# -gt 0 ]]; then
    K=$(echo $k | tr a-z A-Z)
    $SAX -s:inputs/$k -xsl:"$T/peppol/peppol-$k.xsl" -o:out/peppol_$k 2>>out/saxon.log || true
    $SAX -s:inputs/$k -xsl:"$T/cen/EN16931-$K-validation.xslt" -o:out/cen_$k 2>>out/saxon.log || true
  fi
done
python3 "$HERE/oracle.py"
