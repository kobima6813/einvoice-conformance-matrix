"""Per-invoice findings for the GitHub Action. usage: ci_report.py rows.json workdir/inputs [expected.json] [fail-on]"""
import json, re, sys
from decimal import Decimal as D
rows = json.load(open(sys.argv[1])); inp = sys.argv[2]
exp = json.load(open(sys.argv[3])) if len(sys.argv) > 3 and sys.argv[3] else {}
fail_on = (sys.argv[4] if len(sys.argv) > 4 else 'any').strip()
# Peppol rules that only concern Peppol transport/identifiers (not arithmetic or EN 16931 content)
CTX = re.compile(r'^PEPPOL-(EN16931-(R00\d|R010|R020|CL00[678]|P0100|P0112)|COMMON-R0[45]\d)$')
def amt(t, tags): return sum((D(x) for x in re.findall(r'<(?:%s)[^>]*>\s*([-0-9.]+)\s*<' % tags, t)), D(0))
bad = 0; hits = 0
for r in rows:
    errs = set(r['cen_fails'] or []) | {p for p in (r['peppol_fails'] or []) if not CTX.match(p)}
    errs |= {('XSD' if e.startswith('cvc-') else e) for e in (r['kosit_errors'] or [])}
    if r['line_exact_fail'] or r['vat_exact_fail']: errs.add('ARITH-EXACT')
    key = r['file'][:-4]; cid = key.rsplit('__', 1)[-1].split('_')[0]
    want = exp.get(key, exp.get(cid))
    if want is not None:
        t = open(f"{inp}/{r['kind']}/{r['file']}", encoding='utf-8').read()
        if amt(t, 'ram:DuePayableAmount|cbc:PayableAmount') + amt(t, 'ram:TotalPrepaidAmount|cbc:PrepaidAmount') != D(want):
            errs.add('DUE-NE-CHARGED')
    if errs:
        bad += 1; print(r['file'], ','.join(sorted(errs)))
        if fail_on == 'any' or (fail_on != 'none' and errs & set(x.strip() for x in fail_on.split(','))): hits += 1
print(f'{bad}/{len(rows)} invoices with findings; {hits} match fail-on={fail_on}')
sys.exit(1 if hits else 0)
