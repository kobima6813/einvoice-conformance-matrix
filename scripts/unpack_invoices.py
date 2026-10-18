"""Unpack invoices/*.tar.xz (or a directory of generator outputs) into an oracle workdir.

usage: unpack_invoices.py <workdir> [archive-or-dir ...]   (default: invoices/*.tar.xz)
Files are named <generator-config>__<cart-id>.xml; the part before '__' becomes the 'origin'.
"""
import glob, json, os, shutil, sys, tarfile
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
work = sys.argv[1]; srcs = sys.argv[2:] or sorted(glob.glob(os.path.join(root, 'invoices', '*.tar.xz')))
for k in ('cii', 'ubl'): os.makedirs(os.path.join(work, 'inputs', k), exist_ok=True)
idx = []
def add(name, data):
    b = os.path.basename(name)
    if not b.endswith('.xml'): return
    kind = 'ubl' if b'urn:oasis:names:specification:ubl' in data[:4000] else 'cii'
    open(os.path.join(work, 'inputs', kind, b), 'wb').write(data)
    idx.append(dict(file=b, kind=kind, origin=b.split('__')[0]))
for s in srcs:
    if os.path.isdir(s):
        for p in sorted(glob.glob(os.path.join(s, '**', '*.xml'), recursive=True)): add(p, open(p, 'rb').read())
    else:
        with tarfile.open(s) as t:
            for m in t.getmembers():
                if m.isfile(): add(m.name, t.extractfile(m).read())
idx.sort(key=lambda x: x['file'])
json.dump(idx, open(os.path.join(work, 'inputs', 'index.json'), 'w'))
print(len(idx), 'invoices')
