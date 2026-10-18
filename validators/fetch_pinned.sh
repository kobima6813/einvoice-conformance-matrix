#!/usr/bin/env bash
# Download pinned validator artefacts into $EICM_TOOLS (default: <repo>/.tools),
# verify SHA-256 against validators/pins.txt, unpack the XRechnung configuration
# and compile the Peppol schematrons to XSLT with SchXslt.
#   --with-optional   also fetch Mustang-CLI and the FNFE Factur-X XSD/XSLT set
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="${EICM_TOOLS:-$HERE/../.tools}"; mkdir -p "$T"; T="$(cd "$T" && pwd)"
OPT=0; [[ "${1:-}" == "--with-optional" ]] && OPT=1
fail=0
while read -r sha dest url; do
  [[ -z "$sha" || "$sha" == \#* ]] && continue
  [[ "$dest" == optional/* && $OPT -eq 0 ]] && continue
  f="$T/$dest"; mkdir -p "$(dirname "$f")"
  if [[ ! -f "$f" ]] || ! echo "$sha  $f" | sha256sum -c --quiet - 2>/dev/null; then
    curl -fsSL --retry 3 -o "$f.part" "$url" && mv "$f.part" "$f"
  fi
  if echo "$sha  $f" | sha256sum -c --quiet - 2>/dev/null; then echo "ok   $dest"
  else echo "FAIL checksum $dest ($url)" >&2; fail=1; fi
done < "$HERE/pins.txt"
[[ $fail -eq 0 ]] || exit 1
# XRechnung configuration (scenarios.xml + resources)
if [[ ! -f "$T/xr/scenarios.xml" ]]; then
  rm -rf "$T/xr"; mkdir -p "$T/xr"
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$T/xrechnung-3.0.2-validator-configuration-2026-08-31.zip" "$T/xr"
fi
# Peppol BIS 3.0.20 schematron -> XSLT (output differs from run to run only in a dct:created timestamp)
CP="$T/lib/Saxon-HE-12.10.jar:$T/lib/xmlresolver-5.3.3.jar:$T/lib/xmlresolver-5.3.3-data.jar"
for k in ubl cii; do
  K=$(echo $k | tr a-z A-Z)
  if [[ ! -f "$T/peppol/peppol-$k.xsl" ]]; then
    java -cp "$CP" net.sf.saxon.Transform -s:"$T/peppol/PEPPOL-EN16931-$K.sch" \
      -xsl:"jar:file:$T/lib/schxslt-1.10.1.jar!/xslt/2.0/pipeline-for-svrl.xsl" -o:"$T/peppol/peppol-$k.xsl"
  fi
done
echo "validators ready in $T"
