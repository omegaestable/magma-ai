"""rep18137l.py : machine-check the seven remaining Lean lemma statements of gen/rec18137b.lean on the repaired model."""
import sys, random, time
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen')
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import importlib.util
spec = importlib.util.spec_from_file_location('reps', 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen\\rep18137s.py')
sys.argv = ['x', '2500']
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
M = mod.M; J = mod.J; isJ = mod.isJ; size = mod.size; show = mod.show
def a1(t): return t[1] if isJ(t) else t
def a2(t): return t[2] if isJ(t) else t
def Sh(v): return isJ(v) and isJ(v[2]) and v[1] == v[2][2]
def Enc(a, w): return Sh(w) and M.op(a, a1(w)) == a1(a2(w))
def RF(u, x): return (isJ(u) and u[2] == x and M.op(u[1], u[2]) == u) or Enc(u, x)
random.seed(5)
terms = list({t for k in list(M.memo)[:60000] for t in k if size(t) <= 40})
random.shuffle(terms); terms = terms[:1500]
nonfree = [(k, r) for k, r in list(M.memo.items()) if r != J(k[0], k[1])]
print('terms', len(terms), 'nonfree pairs', len(nonfree))
bad = {}
def rec(name, cond, info):
    if not cond:
        bad[name] = bad.get(name, 0) + 1
        if bad[name] <= 2: print('  COUNTEREXAMPLE', name, info)
t0 = time.time()
# encG: op u v = x non-free -> sz x < sz u or sz x < sz v ; also Enc x v and RF u x (soundness re-check)
for (u, v), x in nonfree:
    rec('encG', size(x) < size(u) or size(x) < size(v), (show(u), show(v), show(x)))
    rec('SND', Enc(x, v) and RF(u, x), (show(u), show(v), show(x)))
# H2, H1 on random (x, z) and on pairs from the memo
xs = terms[:400]; zs = terms[400:800]
for x in xs:
    for z in zs[:120]:
        B = M.op(x, z)
        rec('H2', M.op(B, z) == J(B, z), (show(x), show(z)))
        rec('H1', M.op(z, J(B, z)) == J(z, J(B, z)), (show(x), show(z)))
# encD: tg u = 2 -> op u w != op (a2 u) w
for u in [t for t in terms if isJ(t)][:300]:
    for w in zs[:100]:
        rec('encD', M.op(u, w) != M.op(u[2], w), (show(u), show(w)))
# encF: Enc a b -> op a w != op b w  (Enc a b pairs: a = op b' b non-free gives Enc a b)
encpairs = list({(x, k[1]) for k, x in nonfree})[:300]
for (a, b) in encpairs:
    for w in zs[:60]:
        rec('encF', M.op(a, w) != M.op(b, w), (show(a), show(b), show(w)))
# encC: tg u = 2, Enc u x, op (a2 u) z = op x z -> x = a2 u   (Enc u x pairs: u = op y x non-free)
cpairs = list({(x, k[1]) for k, x in nonfree if isJ(x)})[:300]
for (u, x) in cpairs:
    for z in zs[:60]:
        if M.op(u[2], z) == M.op(x, z):
            rec('encC', x == u[2], (show(u), show(x), show(z)))
# CMP: Enc x v and RF u x -> op u v = x   (build v = J z (J (op x z) z); u = J r x, or u with Enc u x via x = J x1 (J (op u x1) x1))
cnt = 0
for x in terms[:500]:
    for z in zs[:20]:
        v = J(z, J(M.op(x, z), z))
        r = random.choice(terms)
        u = J(r, x)
        if RF(u, x):
            cnt += 1; rec('CMP-free', M.op(u, v) == x, (show(u), show(v), show(x)))
    if Sh(x):
        # every u with op u (a1 x) = a1 (a2 x) : from memo entries
        for (uu, w), res in nonfree:
            if w == x[1] and res == x[2][1]:
                for z in zs[:10]:
                    v = J(z, J(M.op(x, z), z))
                    cnt += 1; rec('CMP-enc', M.op(uu, v) == x, (show(uu), show(v), show(x)))
print('CMP instances', cnt)
print('done in', round(time.time() - t0, 1), 's; counterexample counts:', bad if bad else 'NONE')
