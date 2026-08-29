"""Systematic shape x shape coincidence test for the repaired 12234 model (gen/rep12234.py):
x encodes w by z with shape S in 1..6 (which of A',B',C' are decoded), y is random / encodes by x (shape T) /
encodes by A=op(z,x) (shape T), sub-encodings get random shapes.  Every law instance must give x."""
import sys, random
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import importlib.util
spec = importlib.util.spec_from_file_location('rep', 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep12234.py')
sys.argv = ['rep', '200', '200']
rep = importlib.util.module_from_spec(spec); spec.loader.exec_module(rep)
M, g, J, show, size = rep.M, rep.g, rep.J, rep.show, rep.size

def rnd(d=1):
    if d <= 0 or random.random() < 0.4: return g(random.randrange(3))
    return J(rnd(d - 1), rnd(d - 1))

def build(w, u, q, S, depth):
    """return (x, u) with x = enc(w, u, q) of shape S (u may be replaced to force the shape)"""
    if depth <= 0: S = 1
    sub = lambda: random.randrange(1, 7)
    if S in (3, 4, 6):   # A' = op(q, w) decoded: w must encode something by q
        w, q, _ = build(rnd(), q, rnd(), sub(), depth - 1)
    A = M.op(q, w)
    if S in (2, 4):      # C' = op(w, u) decoded: u encodes something by w
        u, _, _ = build(rnd(), w, rnd(), sub(), depth - 1)
    if S in (5, 6):      # B' = op(A', u) decoded: u encodes something by A'
        u, _, _ = build(rnd(), A, rnd(), sub(), depth - 1)
    x = M.encD(w, u, q)
    return x, u, w

fails = []; tested = 0; fired0 = dict(M.fired)
random.seed(5)
for rep_i in range(400):
    for S in range(1, 7):
        w, q = rnd(), rnd()
        x, z, w = build(w, rnd(), q, S, 2)
        if size(x) > 150: continue
        if M.op(z, x) != w: fails.append(('decode', S, x, z, w)); continue
        ys = [('rand', rnd(2))]
        for T in range(1, 7):
            yx, _, _ = build(rnd(), x, rnd(), T, 1); ys.append(('encx%d' % T, yx))
            A = M.op(z, x)
            ya, _, _ = build(rnd(), A, rnd(), T, 1); ys.append(('encA%d' % T, ya))
        for tag, y in ys:
            if size(y) > 150: continue
            r = M.enc(x, y, z); tested += 1
            if r != x: fails.append((tag, S, x, y, z, r))
print('tested', tested, 'fails', len(fails))
print('fired', {k: M.fired.get(k, 0) - fired0.get(k, 0) for k in range(1, 7)})
for f in fails[:4]:
    print(f[0], 'S=%d' % f[1])
    for t in f[2:]: print('  ', show(t))
