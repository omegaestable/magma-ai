"""rep18137s.py [N] : structured (coincidence-targeted) law tests for the repaired 18137 model.
Builds triples through the encoding shapes so that A = y*x and B = x*z are non-free at random depths,
then checks the law with the repaired model and compares every touched pair with the free model."""
import sys, random, time
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen')
import freemodel as fm
from freemodel import normalise, catalog, Free, size
from laws import parse_eq
import importlib.util
spec = importlib.util.spec_from_file_location('rep', 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen\\rep18137.py')
law = normalise(parse_eq(catalog()[18137]))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def isJ(t): return t[0] == 'J'
def msr(a, b):
    m = max(size(a), size(b)); return m * m + size(a) + size(b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

class Model:
    def __init__(self): self.memo = {}; self.fired = {}
    def gated(self, a, b, u, v):
        if msr(a, b) < msr(u, v): return self.op(a, b)
        return J(u, v)
    def enc(self, a, w, U, V):
        return isJ(w) and isJ(w[2]) and w[1] == w[2][2] and self.gated(a, w[1], U, V) == w[2][1]
    def op(self, u, v):
        k = (u, v); r = self.memo.get(k)
        if r is None:
            r = self._op(u, v); self.memo[k] = r
        return r
    def _op(self, u, v):
        if not (isJ(v) and isJ(v[2]) and v[1] == v[2][2]): return J(u, v)
        z = v[1]; B = v[2][1]
        if isJ(u) and self.gated(u[1], u[2], u, v) == u and self.gated(u[2], z, u, v) == B:
            self.fired[1] = self.fired.get(1, 0) + 1; return u[2]
        if isJ(B) and B[2] == z and self.gated(B[1], z, u, v) == B and self.enc(u, B[1], u, v):
            self.fired[2] = self.fired.get(2, 0) + 1; return B[1]
        if isJ(B) and self.gated(u, B[2], u, v) == B[1] and self.gated(J(B[2], B), z, u, v) == B:
            self.fired[3] = self.fired.get(3, 0) + 1; return J(B[2], B)
        p7 = self.gated(u, B, u, v)
        if p7 != J(u, B) and self.gated(p7, z, u, v) == B:
            self.fired[4] = self.fired.get(4, 0) + 1; return p7
        return J(u, v)
    def evp(self, p, s):
        if isinstance(p, str): return s[p]
        return self.op(self.evp(p[0], s), self.evp(p[1], s))

M = Model()
pool = [g(i) for i in range(4)]
def rnd(d):
    if d <= 0 or random.random() < 0.35: return random.choice(pool) if random.random() < 0.7 else g(random.randrange(4))
    return J(rnd(d - 1), rnd(d - 1))
def enc_of(a, d):
    """a term w with Enc a w (w encodes a): w = J w1 (J (op a w1) w1)"""
    w1 = rnd(d)
    return J(w1, J(M.op(a, w1), w1))
def rf_pair(d):
    """(y, x) with op y x non-free: x encodes A, y = J r A (or deeper: y itself a product)"""
    A = rnd(d)
    x = enc_of(A, d)
    y = J(rnd(d), A)
    return y, x, A
def triple(d):
    r = random.random()
    if r < 0.6:
        y, x, A = rf_pair(d)
    else:
        x = rnd(d); y = rnd(d)
    r = random.random()
    if r < 0.3:
        z = rnd(d)
    elif r < 0.6 and isJ(x):
        # B = x.2 (Free(x, B) case) : z encodes B by x
        B = x[2]; z = enc_of(B, d)
    else:
        # Enc x B case : B = J b1 (J (op x b1) b1); z encodes B
        b1 = rnd(d); B = J(b1, J(M.op(x, b1), b1)); z = enc_of(B, d)
    return {'x': x, 'y': y, 'z': z}

random.seed(20260829)
fails = 0; tested = 0; t0 = time.time(); big = 0
for i in range(N):
    d = random.choice([1, 1, 2, 2, 3])
    s = triple(d)
    if max(size(t) for t in s.values()) > 400: big += 1; continue
    try:
        E = M.evp(law[1], s)
    except RecursionError:
        print('RECURSION', {k: show(v) for k, v in s.items()}); fails += 1; continue
    tested += 1
    if E != s['x']:
        fails += 1
        if fails <= 3: print('FAIL', {k: show(v) for k, v in s.items()}, '->', show(E))
    for t in s.values():
        if size(t) <= 60 and len(pool) < 300: pool.append(t)
print('structured: tested', tested, 'skipped-big', big, 'fails', fails, 'fired', M.fired, 'memo', len(M.memo), 'secs', round(time.time() - t0, 1))
F = Free(law)
pairs = [k for k in M.memo if size(k[0]) + size(k[1]) <= 80 and M.memo[k] != J(k[0], k[1])]
pairs2 = [k for k in M.memo if size(k[0]) + size(k[1]) <= 80 and M.memo[k] == J(k[0], k[1])]
random.shuffle(pairs); random.shuffle(pairs2)
mism = 0; checked = 0; t0 = time.time()
for (u, v) in pairs[:3000] + pairs2[:3000]:
    if time.time() - t0 > 300: break
    try: fr = F.op(u, v)
    except Exception: continue
    checked += 1
    if fr != M.memo[(u, v)]:
        mism += 1
        if mism <= 5: print('  MISMATCH u=', show(u), 'v=', show(v), 'model=', show(M.memo[(u, v)]), 'free=', show(fr))
print('free-model comparison: nonfree pairs', len(pairs), 'checked', checked, 'mismatches', mism, 'conflicts', len(F.conflicts), 'secs', round(time.time() - t0, 1))
