"""Check regenerated invoices against the shipped archive, ignoring generator banner comments.
usage: diff_generated.py <regenerated_dir> <invoices/xxx.tar.xz>   (exit 1 on any difference)"""
import os, re, sys, tarfile
new_dir, arc = sys.argv[1], sys.argv[2]
norm = lambda b: re.sub(rb'<!--.*?-->', b'', b)
bad = n = 0
with tarfile.open(arc) as t:
    for m in t.getmembers():
        if not m.isfile(): continue
        n += 1; p = os.path.join(new_dir, os.path.basename(m.name))
        if not os.path.exists(p) or norm(open(p, 'rb').read()) != norm(t.extractfile(m).read()):
            bad += 1; print('differs:', os.path.basename(m.name)) if bad <= 10 else None
print(f'{n - bad}/{n} identical'); sys.exit(1 if bad else 0)
