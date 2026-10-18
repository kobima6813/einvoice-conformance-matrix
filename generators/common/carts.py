"""Load corpus/carts_{b2b,b2c}.json (shop view) into shop_sim order dicts."""
import json, os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shop_sim import r2
def load(path):
    out = []
    for c in json.load(open(path)):
        lines = [dict(name=l['name'], qty=int(l['qty']), unit_gross=D(l['unit_gross']), rate=D(l['rate'])) for l in c['lines']]
        pct = D(c['pct']) if c.get('pct') and D(c['pct']) > 0 else None
        ship = D(c['ship']) if c.get('ship') and D(c['ship']) > 0 else None
        sub = [l['unit_gross'] * l['qty'] for l in lines]
        if pct:
            dt = r2(sum(sub) * pct / 100); al = [r2(s * pct / 100) for s in sub]; al[-1] += dt - sum(al)
        else:
            al = [D(0)] * len(lines)
        for l, s, a in zip(lines, sub, al):
            l['gross'] = s - a; l['disc_gross'] = a; l['shop_tax'] = r2(l['gross'] * l['rate'] / (100 + l['rate']))
        paid = sum(l['gross'] for l in lines) + (ship or 0)
        assert D(c['paid']) == paid, (c['id'], paid, c['paid'])
        out.append(dict(id=c['id'], lines=lines, ship=ship, ship_tax=r2(ship * 19 / 119) if ship else D(0), paid=paid, pct=pct))
    return out
