"""_s9_17286_lem.py -- candidate-lemma census on the LEAN-EXACT mirror.

Lemmas under test (all over every (u,v) pair the oracle stack actually evaluates, plus a
constructed pool with LARGE junk in a1 u -- the defect that has refuted four size claims on
this law):

  NL     : op u v != u
  NSELF  : not (cds u u)
  NPZ    : Cd v -> op (a2 (a2 v)) (a1 v) != a2 (a2 v)
  F2U    : Cd (J z (op x z)) AND op x z != J x z      (is F2's case (U) reachable?)
  F1CD   : Cd (op x z)  with op x z free / decoded    (F1's guard reachability)
"""
import os, importlib.util, collections
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lab', os.path.join(HERE, '_x17286_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
g, J, tg, a1, a2, sz, show, encB, deep, terms = (
    lab.g, lab.J, lab.tg, lab.a1, lab.a2, lab.sz, lab.show, lab.encB, lab.deep, lab.terms)
spec2 = importlib.util.spec_from_file_location('pr', os.path.join(HERE, '_s9_17286_probe.py'))
pr = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(pr)
Mod = pr.Mod

C = collections.Counter()
EX = {}


def note(k, ok, ex=None):
    C[k + ('.ok' if ok else '.BAD')] += 1
    if not ok and k not in EX:
        EX[k] = ex


def sweep_pairs(M):
    for (u, v), (r, tag) in list(M.pairs.items()):
        note('NL', r != u, (u, v, r))
        if M.Cd(v):
            Pv = a2(a2(v))
            if M.op(Pv, a1(v)) == Pv:
                note('NPZ', False, (u, v))
            else:
                note('NPZ', True)
    # cds u u over every term seen anywhere
    ts = set()
    for (u, v) in M.pairs:
        ts.add(u); ts.add(v)
    for t in list(ts)[:4000]:
        if M.cds(t, t):
            note('NSELF', False, (t,))
        else:
            note('NSELF', True)


def chains(M, xs, ys, zs, tagn, cap=200000):
    k = 0
    for x in xs:
        for y in ys:
            for z in zs:
                if k > cap:
                    return
                k += 1
                try:
                    P = M.op(x, z)
                    Q = M.op(z, P)
                    B = M.op(z, Q)
                    A = M.op(y, x)
                    top = M.op(A, B)
                except RecursionError:
                    continue
                note('law', top == x, (x, y, z, top))
                note('F1', Q == J(z, P), (x, z, Q))
                note('F2', B == J(z, Q), (x, z, B))
                Pfree = (P == J(x, z))
                if M.Cd(J(z, P)):
                    C['F2site.%s.%s' % (tagn, 'Pfree' if Pfree else 'Pdec')] += 1
                    if not Pfree and 'F2U' not in EX:
                        EX['F2U'] = (x, y, z)
                if M.Cd(P):
                    C['F1site.%s.%s' % (tagn, 'Pfree' if Pfree else 'Pdec')] += 1
                    if not Pfree and 'F1D' not in EX:
                        EX['F1D'] = (x, y, z)


def pool_small():
    return terms(7, 2)


def pool_towers(junk):
    out = []
    for base in (g(0), J(g(0), g(1))):
        ws = [g(20 + i) for i in range(4)]
        t = base
        out.append(t)
        for w in ws:
            t = encB(t, w)
            out.append(t)
            out.append(J(junk, t))
            out.append(a2(t))
            out.append(a2(a2(t)))
    return out


def run():
    M = Mod()
    T = pool_small()
    small = [t for t in T if sz(t) <= 7]
    chains(M, small, small, small, 'exh', cap=200000)
    for junk in (g(9), deep(13), deep(31)):
        P = pool_towers(junk)
        chains(M, P, P, P, 'tow', cap=40000)
    sweep_pairs(M)
    print('pairs evaluated:', len(M.pairs), 'cycles', M.cycles, 'fired', dict(M.fired))
    for k in sorted(C):
        print('  %-24s %d' % (k, C[k]))
    print()
    for k, v in EX.items():
        print('  EX %-8s %s' % (k, ' | '.join(show(t) for t in v)))


if __name__ == '__main__':
    run()
