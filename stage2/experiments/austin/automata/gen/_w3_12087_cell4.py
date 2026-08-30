import sys, os
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(D, 'gen', '_w3_12087_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
op, sz, show, tg = lab.op, lab.sz, lab.show, lab.tg
terms = lab.terms
def kind(u, v):
    r = op(u, v)
    if r == ('J', u, v): return 'F'
    if r == ('E', u, v): return 'T'
    return 'D'
pool = terms(5, 2)
found = []
for x in pool:
    for y in pool:
        for z in pool:
            try:
                N1 = op(y, x); N2 = op(N1, z); N3 = op(x, z); V = op(N2, N3)
                k = (kind(y, x), kind(N1, z), kind(x, z), kind(N2, N3))
                if k == ('F', 'D', 'F', 'F'):
                    found.append((x, y, z, N1, N2, N3, V, op(y, V)))
                    if len(found) >= 3: raise StopIteration
            except (RecursionError, StopIteration) as e:
                if isinstance(e, StopIteration): break
        else: continue
        break
    else: continue
    break
print('cell (F,D,F,F) instances found:', len(found))
for (x, y, z, N1, N2, N3, V, R) in found:
    print('  x=%s  y=%s  z=%s' % (show(x), show(y), show(z)))
    print('    N1=%s  N2=%s  N3=%s' % (show(N1), show(N2), show(N3)))
    print('    V=%s  tg V=%d' % (show(V), tg(V)))
    print('    op y V = %s   == x ? %s' % (show(R), R == x))
