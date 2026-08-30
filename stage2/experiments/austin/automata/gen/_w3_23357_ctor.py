"""23357: the CONSTRUCTED-GUARD suite -- one family per rule whose op-guard demands that some inner
product be FREE.  Each family draws that inner pair from the DECODING pairs, which is the case no
sampler reaches (the guard then fails and a different rule must cover the cell).

Derivation: read the per-cell top-rule map (gen/_w3_23357_h3.out), take the guard the winning rule
needs, and ask what makes it false.
  C1  cell (AF,UF,BD,VF) -> rule `A0s,B1s|rd:A0`, guard 2  `a1 y = op (a2 y) B`.
      With B decoded through rule 1 at (y,z): y = J (J y1 x1) y1, z = J x1 (J y1 r), B = x1,
      so the guard is `J y1 x1 = op y1 x1`.  Draw (y1,x1) DECODING.
  C2  cell (AF,UF,BF,VD) -> rule `RD`, guard `a1 x = op (a2 x) V`.
      With V decoded through an L-rule at (x,B): x = J (J P q) P, B = J q (J P r), V = q,
      so the guard is `J P q = op P q`.  Draw (P,q) DECODING.  (The `As`-at-(x,B) route needs the
      same product free, so one family covers both.)
POSITIVE CONTROL: every family asserts the cell it aims at was actually produced.
"""
import sys, collections
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, trace as tr, fuzz as fz
from freemodel import size, rand_term
import importlib.util, random
G = D + '/gen/'
show = tr.show; J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
sv = list(sys.argv); sys.argv = [sys.argv[0]]
r12 = importlib.util.spec_from_file_location('_x23357_rep', G + '_x23357_rep.py')
M12 = importlib.util.module_from_spec(r12); r12.loader.exec_module(M12)
s2 = importlib.util.spec_from_file_location('_w3_23357_sets2', G + '_w3_23357_sets2.py')
S = importlib.util.module_from_spec(s2); s2.loader.exec_module(S)
law = M12.law; TAG12 = {r[2]: r for r in M12.rules}
F4 = S.SETS['f4']
SETS = {
    'f4':        F4,
    'g5=f4+B1s': [F4[0], TAG12['B1s'], F4[1], F4[2], F4[3]],
    'g6':        [F4[0], TAG12['B1s'], F4[1], TAG12['A0s,B1s'], F4[2], F4[3]],
    'full12':    list(M12.rules),
}

rng = random.Random(3)
C0 = cf.Closed(law, M12.rules)
pool = [g(i) for i in range(4)]
for d in range(3):
    for u, v in fz.instances(M12.rules, pool, 14, d, C0):
        for t in (u, v):
            if size(t) <= 60 and t not in pool: pool.append(t)
        try:
            r = C0.op(u, v)
            if size(r) <= 60 and r not in pool: pool.append(r)
        except RecursionError: pass
for _ in range(200):
    t = rand_term(rng.randint(1, 4), 3)
    if t not in pool: pool.append(t)
DEC = [(a, b) for a in pool for b in pool if C0.op(a, b) != J(a, b)]
SM = [t for t in pool if size(t) <= 12]
print('pool %d  decoding pairs %d' % (len(pool), len(DEC)), flush=True)


def triples(fam):
    out = []
    for (p, q) in DEC[:400]:
        for r in SM[:5]:
            if fam == 'C1':                       # y = J (J y1 x1) y1 with op y1 x1 decoded
                y = J(J(p, q), p); z = J(q, J(p, r))
                for x in (g(7), g(8)):
                    out.append((x, y, z))
            else:                                 # C2: x = J (J P q) P with op P q decoded
                x = J(J(p, q), p); y = q; z = J(p, r)
                out.append((x, y, z))
    return out


for fam in ('C1', 'C2'):
    T = triples(fam)
    print('\n--- family %s : %d constructed triples ---' % (fam, len(T)), flush=True)
    for nm, rules in SETS.items():
        bad = 0; n = 0; cells = collections.Counter(); worst = None
        for (x, y, z) in T:
            C = cf.Closed(law, rules)
            try:
                A = C.op(y, x); U = C.op(A, y); B = C.op(y, z); V = C.op(x, B); top = C.op(U, V)
            except RecursionError:
                continue
            n += 1
            cells[(('AD' if A != J(y, x) else 'AF'), ('UD' if U != J(A, y) else 'UF'),
                   ('BD' if B != J(y, z) else 'BF'), ('VD' if V != J(x, B) else 'VF'))] += 1
            if top != x:
                bad += 1
                t = sum(size(q) for q in (x, y, z))
                if worst is None or t < worst[0]: worst = (t, x, y, z)
        tgt = 'BD' if fam == 'C1' else 'VD'
        ctl = sum(c for k, c in cells.items() if tgt in k)
        print('  %-12s tested %-5d BAD %-5d  | control: cell with %s produced %d  %s'
              % (nm, n, bad, tgt, ctl, dict(list(cells.most_common(3)))), flush=True)
        if worst and nm == 'f4':
            t, x, y, z = worst
            print('     smallest bad: x=%s  y=%s  z=%s' % (show(x)[:110], show(y)[:160], show(z)[:110]), flush=True)
