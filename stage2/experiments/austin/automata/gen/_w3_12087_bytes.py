import re, sys
p = sys.argv[1]
t = open(p, encoding='utf-8').read()
# split on top-level declaration starts
idx = [m.start() for m in re.finditer(r'(?m)^(theorem|def|instance|inductive|abbrev|namespace|end|import|set_option|@\[)', t)]
idx.append(len(t))
rows = []
for a, b in zip(idx, idx[1:]):
    seg = t[a:b]
    name = seg.split('\n')[0][:70]
    rows.append((len(seg.encode('utf-8')), name))
rows.sort(reverse=True)
tot = len(t.encode('utf-8'))
print('total', tot)
for n, name in rows[:22]:
    print('%6d  %5.1f%%  %s' % (n, 100.0*n/tot, name))
