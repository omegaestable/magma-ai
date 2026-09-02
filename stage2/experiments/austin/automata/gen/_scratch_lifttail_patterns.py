import sys, collections
sys.path.insert(0, 'stage2/experiments/austin/automata/gen')
import _x32281_cellgen as m

op, J, a1, a2, sz = m.op, m.J, m.a1, m.a2, m.sz
free = lambda u, v: op(u, v) == J(u, v)
cells = []
for (x, y), P in list(m.C.memo.items()):
    if free(x, y):
        continue
    b = a2(y)
    try:
        C = op(op(P, b), b)
        D = op(x, C)
    except RecursionError:
        continue
    if a1(y) == D and not free(x, C):
        cells.append((x, y, P, b, C, D))

cnt = collections.Counter()
rows = []
zs = [m.g(0), m.g(1), m.g(2), m.J(m.g(0),m.g(1))]
for x,y,P,b,C,D in cells:
    c = a2(C); Cp = op(op(D,c),c); qlo=op(D,C); Q=op(P,y)
    cat = m.which(x,C)
    vals = {
        'C=P': C==P, 'Cp=D': Cp==D, 'Qfree':free(P,y),
        'qlo_free': free(D,C), 'Cp_free': free(op(D,c),c),
        'guard2_free': free(x,Cp),
    }
    cnt[(cat, tuple(k for k,v in vals.items() if v))] += 1
    if len(rows)<12 and all(r[0]!=cat for r in rows):
        rows.append((cat, vals, [sz(t) for t in (x,y,P,b,C,D,c,Cp,qlo,Q)]))
print('cells',len(cells))
for k,v in cnt.most_common(20): print(v,k)
for r in rows: print('ROW',r)
