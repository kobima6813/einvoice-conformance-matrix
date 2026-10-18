"""Rebuild the synthetic corpus deterministically.

carts_b2c.json  seed 42, small quantities   (QTY=b2c)
carts_b2b.json  seed 43, wholesale quantities (QTY=b2b)
expected_paid.json         amount the simulated shop charged per cart
ref_en16931_rounding.json  reference EN 16931 totals (net unit price, line allowance,
                           VAT per category, BT-114 rounding to the charged amount)
carts_net.json             net-price view of the same carts (input for generators
                           that compute their own totals, e.g. Mustang)

Usage: python3 corpus/build_corpus.py [outdir]   (default: corpus/)
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'generators', 'common'))
import shop_sim
out = sys.argv[1] if len(sys.argv) > 1 else HERE
os.makedirs(out, exist_ok=True)
carts, ref, net, paid = {}, [], [], {}
for seg, seed in (('b2b', 43), ('b2c', 42)):
    os.environ['QTY'] = seg
    rng = random.Random(seed); rows = []
    for i in range(300):
        o = shop_sim.cart(rng); cid = f'{seg}{i:04d}'
        rows.append(dict(id=cid, paid=str(o['paid']), pct=str(o['pct'] or 0), ship=str(o['ship'] or '0'),
                         lines=[dict(name=l['name'], qty=l['qty'], unit_gross=str(l['unit_gross']), rate=str(l['rate'])) for l in o['lines']]))
        L, tax, T, _ = shop_sim.S_en16931(o, rounding=True)
        s = lambda d: {k: ([str(x) for x in v] if isinstance(v, list) else str(v)) for k, v in d.items()}
        ref.append(dict(id=cid, paid=str(o['paid']), L=[s(x) for x in L], tax=[s(x) for x in tax], T=s(T)))
        net.append(dict(id=cid, paid=str(o['paid']), lines=[dict(name=x['name'], qty=str(x['qty']), price=str(x['net_price']),
                        allow=[str(a) for a in x.get('allow', [])], rate=str(x['rate'])) for x in L]))
        paid[cid] = str(o['paid'])
    carts[seg] = rows
for seg in carts: json.dump(carts[seg], open(f'{out}/carts_{seg}.json', 'w'))
json.dump(ref, open(f'{out}/ref_en16931_rounding.json', 'w'))
json.dump(net, open(f'{out}/carts_net.json', 'w'))
json.dump(paid, open(f'{out}/expected_paid.json', 'w'))
print('wrote', out)
