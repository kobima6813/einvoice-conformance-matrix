"""Aggregate oracle rows into the conformance matrix.

usage: matrix.py <oracle_rows.json> <workdir/inputs> <expected_paid.json> <out-prefix> [platform_order_totals.json]
Writes <out-prefix>.csv and <out-prefix>.md.

Columns (per generator configuration x segment):
  kosit_accept_pct      KoSIT 1.6.3 + XRechnung 3.0.2 configuration returns 'accept'.
                        0 also when no XRechnung scenario matches (Peppol BIS, Factur-X EXTENDED):
                        that is "not applicable", not a rejection; see kosit_nomatch_pct.
  kosit_nomatch_pct     no KoSIT scenario matched the document.
  xsd_invalid_pct       KoSIT reports a schema error (cvc-* message).
  cen_calc_fail_pct     CEN EN16931 XSLT fails a calculation rule (BR-CO-10..BR-CO-16, BR-S-08/09 and
                        equivalents for other categories).
  peppol_R120_fail_pct  Peppol BIS 3.0.20 PEPPOL-EN16931-R120 (line net = qty x price / base +/- line
                        allowances/charges) fails.
  due_ne_order_pct      DuePayableAmount (BT-115) + PrepaidAmount (BT-113) differs from the order total
                        the customer was charged. For WooCommerce/Odoo this is the platform's own order
                        total (invoices/platform_order_totals.json); for libraries it is the simulated
                        shop's charged amount (corpus/expected_paid.json).
  due_ne_sim_pct        same, but always against the simulated shop's charged amount. Platforms that
                        recompute the cart (coupon/discount rounding) differ from the simulator by design,
                        so this column is informational only.
"""
import csv, json, re, sys, collections
from decimal import Decimal as D
rows = json.load(open(sys.argv[1])); inp = sys.argv[2]; exp = json.load(open(sys.argv[3])); outp = sys.argv[4]
plat = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else {}
CALC = re.compile(r'^BR-(CO-1[0-6]|[A-Z]{1,2}-0[89])$')
def amount(text, tags):
    return sum((D(x) for x in re.findall(r'<(?:%s)[^>]*>\s*([-0-9.]+)\s*<' % tags, text)), D(0))
G = collections.OrderedDict()
for r in rows:
    cid = r['file'].rsplit('__', 1)[1][:-4]; seg = cid[:3]
    t = open(f"{inp}/{r['kind']}/{r['file']}", encoding='utf-8').read()
    due = amount(t, 'ram:DuePayableAmount|cbc:PayableAmount'); pre = amount(t, 'ram:TotalPrepaidAmount|cbc:PrepaidAmount')
    k = (r['origin'], seg); g = G.setdefault(k, collections.Counter())
    g['n'] += 1
    g['kosit_accept'] += r['kosit'] == 'accept'
    g['kosit_nomatch'] += bool(r['kosit_nomatch'])
    g['xsd_invalid'] += any(e.startswith('cvc-') or 'xsd' in e.lower() or 'schema' in e.lower() for e in (r['kosit_errors'] or []))
    g['cen_calc_fail'] += any(CALC.match(x) for x in (r['cen_fails'] or []))
    g['peppol_R120_fail'] += 'PEPPOL-EN16931-R120' in (r['peppol_fails'] or [])
    g['due_ne_sim'] += (due + pre) != D(exp[cid])
    g['due_ne_order'] += (due + pre) != D(plat.get(r['file'][:-4], exp[cid]))
cols = ['kosit_accept', 'kosit_nomatch', 'xsd_invalid', 'cen_calc_fail', 'peppol_R120_fail', 'due_ne_order', 'due_ne_sim']
pct = lambda g, c: round(100.0 * g[c] / g['n'], 1)
order = sorted(G, key=lambda k: (k[0].split('-')[0], k[0], k[1]))
with open(outp + '.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['generator', 'segment', 'n'] + [c + '_pct' for c in cols])
    for k in order: w.writerow([k[0], k[1], G[k]['n']] + [pct(G[k], c) for c in cols])
with open(outp + '.md', 'w') as f:
    f.write('| generator / config | seg | n | KoSIT accept % | no KoSIT scenario % | XSD invalid % | CEN calc fail % | Peppol R120 fail % | due ≠ order total % | due ≠ simulated charge % |\n')
    f.write('|---|---|---|---|---|---|---|---|---|---|\n')
    for k in order: f.write(f"| {k[0]} | {k[1]} | {G[k]['n']} | " + ' | '.join(str(pct(G[k], c)) for c in cols) + ' |\n')
# family totals used in the README headline
fam = collections.Counter(); famn = collections.Counter()
for (o, s), g in G.items():
    famn[o] += g['n']
    for c in cols: fam[(o, c)] += g[c]
json.dump({o: {'n': famn[o], **{c: fam[(o, c)] for c in cols}} for o in famn}, open(outp + '_totals.json', 'w'), indent=1, sort_keys=True)
print(open(outp + '.md').read())
