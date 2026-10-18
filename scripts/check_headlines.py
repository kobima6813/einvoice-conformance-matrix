"""Compare a freshly computed matrix with the committed one and print the headline numbers.
usage: check_headlines.py <new matrix.csv> <committed results/matrix.csv>   (exit 1 on any difference)"""
import csv, sys
new = {(r['generator'], r['segment']): r for r in csv.DictReader(open(sys.argv[1]))}
old = {(r['generator'], r['segment']): r for r in csv.DictReader(open(sys.argv[2]))}
diff = [k for k in old.keys() | new.keys() if old.get(k) != new.get(k)]
def agg(prefix, col, seg=None):
    rows = [r for k, r in new.items() if k[0].startswith(prefix) and (seg is None or k[1] == seg)]
    n = sum(int(r['n']) for r in rows); x = sum(round(float(r[col]) * int(r['n']) / 100) for r in rows)
    return f'{x}/{n} ({100 * x / n:.1f}%)' if n else 'n/a'
print('WooCommerce PDF Invoices 5.16.4 Factur-X, XSD-invalid:', agg('wcpdf5164-fx', 'xsd_invalid_pct'))
print('Odoo 19 Factur-X round_globally, CEN calc rule fail  :', agg('odoo19-fx-round_globally', 'cen_calc_fail_pct'))
print('Odoo 19 Factur-X B2B, Peppol R120 fail (both modes)  :', agg('odoo19-fx-', 'peppol_R120_fail_pct', 'b2b'))
for seg in ('b2b', 'b2c'):
    r = new.get(('mustang2.26.0-auto-totals-xrechnung', seg))
    if r: print(f'Mustang 2.26.0 auto totals {seg}: KoSIT accept {r["kosit_accept_pct"]}%, due != charged {r["due_ne_order_pct"]}%')
if diff:
    print('MISMATCH vs committed matrix:', sorted(diff)); sys.exit(1)
print(f'OK: {len(new)} rows identical to the committed matrix')
