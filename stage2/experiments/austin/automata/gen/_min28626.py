import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
import leangen

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk28626.py')
src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']
A, B = law[1]

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def test(y, verbose=False):
    C = cf.Closed(law, rules)
    x = ('J', ('J', ('g', 1), y), y)   # x.1 = J(g1, y), x.2 = y  (the coincidence shape found)
    z = x
    s = {'x': x, 'y': y, 'z': z}
    lhs = C.op(C.evp(A, s), C.evp(B, s))
    ok = (lhs == x)
    if verbose or not ok:
        print('y=', show(y), 'size', size(y), 'x=', show(x), 'OK' if ok else 'FAIL got=%s' % (show(lhs) if size(lhs) < 100 else '<size %d>' % size(lhs)))
    return ok

# small pool of y candidates, increasing size
pool = [('g', 0), ('g', 1), ('g', 2)]
for d in range(4):
    newpool = []
    for t in pool:
        newpool.append(t)
    pool = newpool
    if d > 0:
        pool = pool + [('J', a, b) for a in pool[:6] for b in pool[:6]]
    pool = pool[:40]

found = []
for y in pool:
    if size(y) > 12: continue
    ok = test(y)
    if not ok: found.append(y)

print('tested', len(pool), 'fails', len(found))
for y in found[:5]:
    print(' FAIL y=', show(y))

print("--- confirm original failing y ---")
y_found = ('J', ('J', ('J', ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1))), ('g', 1)), ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1)))), ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1))))
print('size', size(y_found))
test(y_found, verbose=True)

print("--- minimize ---")
def subst_at(t, path, val):
    if not path: return val
    if path[0] == 0: return ('J', subst_at(t[1], path[1:], val), t[2])
    return ('J', t[1], subst_at(t[2], path[1:], val))

def all_paths(t, path=()):
    if t[0] == 'g': return [path]
    return [path] + all_paths(t[1], path+(0,)) + all_paths(t[2], path+(1,))

def get_at(t, path):
    for step in path:
        t = t[1] if step == 0 else t[2]
    return t

cur = y_found
changed = True
while changed:
    changed = False
    for path in sorted(all_paths(cur), key=lambda p: -len(p)):
        sub = get_at(cur, path)
        if sub[0] == 'g' and sub[1] in (0,1,2): continue  # already minimal-ish
        for repl in [('g',0),('g',1),('g',2)]:
            cand = subst_at(cur, path, repl)
            if not test(cand):
                cur = cand; changed = True; break
        if changed: break

print('minimized y =', show(cur), 'size', size(cur))
test(cur, verbose=True)

print("--- template test: y = J(J(J(w,g1),w),w) ---")
def ytempl(w):
    return ('J', ('J', ('J', w, ('g',1)), w), w)

for w in [('g',0), ('g',1), ('g',2), ('J',('g',0),('g',1)), ('J',('g',1),('g',0)), ('J',('g',1),('g',1)), ('J',('g',1),('g',2))]:
    y = ytempl(w)
    ok = test(y)
    print('w=', show(w), 'size(y)=', size(y), 'OK' if ok else 'FAIL')
