import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L
gen = L.g_H3(5, 3); bad = []; cells = {}
for i in range(12000):
    x, y, z = next(gen)
    try:
        pr = L.prof(x, y, z); r = L.chain(x, y, z)[4]
    except RecursionError: continue
    c = cells.setdefault(pr, [0, 0]); c[0] += 1
    if r != x: c[1] += 1; bad.append((x, y, z))
print('H3 n=12000 BAD=%d cells=%d' % (len(bad), len(cells)))
for k in sorted(cells, key=lambda k: -cells[k][1])[:6]:
    print('   %-18s %6d  %d bad' % (','.join(k), cells[k][0], cells[k][1]))
want = sys.argv[1] if len(sys.argv) > 1 else None
sel = [t for t in bad if want is None or ','.join(L.prof(*t)) == want]
for x, y, z in sorted(sel, key=lambda t: sum(L.sz(q) for q in t))[:2]:
    P, Q, A, C, R = L.chain(x, y, z)
    print('--- prof=%s' % ','.join(L.prof(x, y, z)))
    print('   x=%s' % L.show(x)); print('   y=%s' % L.show(y)); print('   z=%s' % L.show(z))
    print('   P=%s' % L.show(P)); print('   Q=%s' % L.show(Q))
    print('   A=%s' % L.show(A)); print('   C=%s' % L.show(C)); print('   R=%s' % L.show(R))
    print('   where is x?  a1 u=%s  a2 u=%s  a1(a2 u)=%s  a2(a2 u)=%s' %
          (L.show(L.a1(y))[:40], L.show(L.a2(y))[:40], L.show(L.a1(L.a2(y)))[:40], L.show(L.a2(L.a2(y)))[:40]))
    v = C
    print('   in v:  a1 v=%s  a2 v=%s  a1(a2 v)=%s  a2(a2 v)=%s' %
          (L.show(L.a1(v))[:40], L.show(L.a2(v))[:40], L.show(L.a1(L.a2(v)))[:40], L.show(L.a2(L.a2(v)))[:40]))
