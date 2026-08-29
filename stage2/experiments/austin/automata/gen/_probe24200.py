import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import freemodel as fm
from freemodel import normalise, catalog, rand_term, size
from laws import parse_eq

eq = 24200
cat = catalog(); law = normalise(parse_eq(cat[eq]))
import importlib.util
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk%d.py' % eq)
src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']

class Tracing(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules)
        self.log = []
    def op(self, u, v):
        key = (u, v)
        if key in self.memo: return self.memo[key]
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key)
        res = None; which = None
        for i, (conds, x, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(x, u, v)
                if r is not None:
                    res = r; which = i; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        self.memo[key] = res
        self.log.append((u, v, which, res))
        return res

random.seed(24200)
fire_at = {'T1': set(), 'T2': set(), 'T3': set(), 'T4': set(), 'final': set()}
counts = {k: {} for k in fire_at}
N = 30000
pool_depth = 3
examples = {}
for i in range(N):
    # bias: sometimes reuse subterms across x,y,z to create coincidences
    mode = i % 5
    if mode == 0:
        x = rand_term(pool_depth); y = rand_term(pool_depth); z = rand_term(pool_depth)
    elif mode == 1:
        x = rand_term(pool_depth); y = x if random.random()<0.3 else rand_term(pool_depth); z = rand_term(pool_depth)
    elif mode == 2:
        # x built from y
        y = rand_term(pool_depth); x = ('J', y, rand_term(pool_depth)) if random.random()<0.5 else ('J', rand_term(pool_depth), y)
        z = rand_term(pool_depth)
    elif mode == 3:
        z = rand_term(pool_depth); x = ('J', z, rand_term(pool_depth)) if random.random()<0.5 else ('J', rand_term(pool_depth), z)
        y = rand_term(pool_depth)
    else:
        x = rand_term(pool_depth+1); y = rand_term(pool_depth+1); z = rand_term(pool_depth+1)
    C = Tracing(law, rules)
    t1 = C.op(y, x)
    t2 = C.op(t1, x)
    t3 = C.op(x, z)
    t4 = C.op(t3, z)
    final = C.op(t2, t3 if False else t4)
    for name, val in (('T1', t1), ('T2', t2), ('T3', t3), ('T4', t4)):
        pass
    # figure out which rule index fired for each, by looking at log entries matching (u,v)
    def which_for(u, v):
        for (lu, lv, w, r) in C.log:
            if lu == u and lv == v:
                return w
        return None
    w1 = which_for(y, x)
    w2 = which_for(t1, x)
    w3 = which_for(x, z)
    w4 = which_for(t3, z)
    wf = which_for(t2, t4)
    for name, w in (('T1', w1), ('T2', w2), ('T3', w3), ('T4', w4), ('final', wf)):
        if w is not None:
            fire_at[name].add(w)
            counts[name][w] = counts[name].get(w, 0) + 1
            if w not in examples.get(name, {}):
                examples.setdefault(name, {})[w] = (x, y, z)
    if final != law and False:
        pass
    if t2 == law:
        pass
    # sanity: final should equal x always (validated)
    fx = final
    if fx != x:
        print("MISMATCH", i, x, y, z, final)
        break

print("rules that fire (0-indexed) at each chain product:")
for name in ('T1','T2','T3','T4','final'):
    idxs = sorted(fire_at[name])
    print(' ', name, '-> rule indices', [i+1 for i in idxs], 'counts', {k+1:v for k,v in counts[name].items()})
print("total samples", N)
