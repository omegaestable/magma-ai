import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L
lv = int(sys.argv[1]) if len(sys.argv) > 1 else 1
gen = L.g_desc(lv, 7, False, 3); bad = []; cells = {}
for i in range(600):
    x, y, z = next(gen)
    try:
        pr = L.prof(x, y, z); r = L.chain(x, y, z)[4]
    except RecursionError: continue
    c = cells.setdefault(pr, [0, 0]); c[0] += 1
    if r != x: c[1] += 1; bad.append((x, y, z))
print('descent lv=%d n=600 BAD=%d cells=%d' % (lv, len(bad), len(cells)))
for k in sorted(cells, key=lambda k: -cells[k][1])[:6]:
    print('   %-18s %6d  %d bad' % (','.join(k), cells[k][0], cells[k][1]))
for x, y, z in sorted(bad, key=lambda t: sum(L.sz(q) for q in t))[:1]:
    P, Q, A, C, R = L.chain(x, y, z)
    print('--- prof=%s   sz x=%d y=%d' % (','.join(L.prof(x, y, z)), L.sz(x), L.sz(y)))
    print('   x=%s' % L.show(x)[:150]); print('   y=%s' % L.show(y)[:150])
    print('   P=%s' % L.show(P)[:150]); print('   Q=%s' % L.show(Q)[:150])
    print('   C=%s' % L.show(C)[:150])
    print('   u=y: a1=%s | a2=%s | a1a2=%s | a2a2=%s' % (L.show(L.a1(y))[:45], L.show(L.a2(y))[:45],
          L.show(L.a1(L.a2(y)))[:45], L.show(L.a2(L.a2(y)))[:45]))
    print('   v=C: a1a2=%s | a2a2=%s' % (L.show(L.a1(L.a2(C)))[:45], L.show(L.a2(L.a2(C)))[:45]))
