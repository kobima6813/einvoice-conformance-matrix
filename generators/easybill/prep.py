"""Write reference EN 16931 lines/VAT/totals (shop_sim.S_en16931, rounding=True) as JSON for the PHP driver.
usage: python3 prep.py <corpus_dir> <out.json>"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from carts import load
from shop_sim import S_en16931
s = lambda x: format(x, 'f') if x is not None else None
res = []
for seg in ('b2b', 'b2c'):
    for o in load(f'{sys.argv[1]}/carts_{seg}.json'):
        L, tax, T, _ = S_en16931(o, rounding=True)
        res.append(dict(id=o['id'], lines=[dict(name=l['name'], qty=s(l['qty']), price=s(l['net_price']), allow=[s(a) for a in l.get('allow', [])], net=s(l['line_net']), rate=s(l['rate'])) for l in L],
                        tax=[dict(rate=s(t['rate']), basis=s(t['basis']), tax=s(t['tax'])) for t in tax], tot={k: s(v) for k, v in T.items()}))
json.dump(res, open(sys.argv[2], 'w'))
