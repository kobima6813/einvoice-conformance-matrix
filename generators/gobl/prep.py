"""Write the shop view of each cart (gross unit prices, % coupon, gross shipping) as JSON for the Go driver.
usage: python3 prep.py <corpus_dir> <out.json>"""
import json, sys
res = []
for seg in ('b2b', 'b2c'):
    for c in json.load(open(f'{sys.argv[1]}/carts_{seg}.json')): res.append(c)
json.dump(res, open(sys.argv[2], 'w'))
