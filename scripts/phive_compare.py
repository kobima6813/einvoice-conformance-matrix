"""Compare phive (XRechnung 3.0.2) verdicts with KoSIT per generator configuration.
usage: phive_compare.py <workdir> <out.csv>   Only invoices declaring an XRechnung 3.0 profile (BT-24) are compared."""
import json, sys, collections, csv
w = sys.argv[1]; rows = {r['file']: r for r in json.load(open(f'{w}/out/oracle_rows.json'))}
S = collections.defaultdict(lambda: dict(n=0, phive_ok=0, kosit_ok=0, agree=0, rules=collections.Counter()))
for l in open(f'{w}/out/phive.jsonl'):
    p = json.loads(l); r = rows[p['file']]
    if 'xrechnung' not in (r.get('profile') or ''): continue
    s = S[r['origin']]; s['n'] += 1; k = r['kosit'] == 'accept'
    s['phive_ok'] += p['valid']; s['kosit_ok'] += k; s['agree'] += (p['valid'] == k)
    s['rules'].update(p['errors'])
with open(sys.argv[2], 'w', newline='') as f:
    c = csv.writer(f); c.writerow(['generator', 'n_xrechnung', 'kosit_accept', 'phive_valid', 'verdicts_agree', 'top_phive_rules'])
    for o in sorted(S):
        s = S[o]; c.writerow([o, s['n'], s['kosit_ok'], s['phive_ok'], s['agree'], ' '.join(f'{k}:{v}' for k, v in s['rules'].most_common(4))])
print(open(sys.argv[2]).read())
