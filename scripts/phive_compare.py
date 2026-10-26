"""Compare phive verdicts with KoSIT per generator configuration.
usage: phive_compare.py <workdir> <out.csv>
XRechnung documents (BT-24) are checked with phive XRechnung 3.0.2; all others with plain EN 16931 1.3.16.
verdicts_agree counts only files for which KoSIT has a scenario."""
import json, sys, collections, csv
w = sys.argv[1]; rows = {r['file']: r for r in json.load(open(f'{w}/out/oracle_rows.json'))}
S = collections.defaultdict(lambda: dict(n=0, nomatch=0, phive_ok=0, kosit_ok=0, agree=0, rules=collections.Counter()))
for l in open(f'{w}/out/phive.jsonl'):
    p = json.loads(l); r = rows[p['file']]
    s = S[(r['origin'], p.get('rule_set', 'xrechnung-3.0.2'))]; s['n'] += 1; k = r['kosit'] == 'accept'
    s['phive_ok'] += p['valid']
    if r.get('kosit_nomatch'): s['nomatch'] += 1; s['rules'].update(p['errors']); continue  # no KoSIT scenario: nothing to compare
    s['kosit_ok'] += k; s['agree'] += (p['valid'] == k)
    s['rules'].update(p['errors'])
with open(sys.argv[2], 'w', newline='') as f:
    c = csv.writer(f, lineterminator='\n'); c.writerow(['generator', 'phive_rule_set', 'n', 'kosit_no_scenario', 'kosit_accept', 'phive_valid', 'verdicts_agree', 'top_phive_rules'])
    for o in sorted(S):
        s = S[o]; c.writerow([o[0], o[1], s['n'], s['nomatch'], s['kosit_ok'], s['phive_ok'], s['agree'], ' '.join(f'{k}:{v}' for k, v in s['rules'].most_common(4))])
print(open(sys.argv[2]).read())
