"""23357 f4: forcing census with POSITIVE CONTROLS, per-rule firing counts, and the H3 family.

Three coordinator checks in one harness:
 1. positive control -- every family reports which rules it actually fired; a family that never fires
    rule k has tested nothing about k, however many assignments it ran;
 2. per-rule / per-family firing counts, and whether the descent saturates in the nesting level;
 3. H3 -- `y` (and `z`, and `x`) built as a genuine ENCODING BY x / BY y, i.e. the law's own variable
    occurs as the decoder inside another variable.  No random pool contains that.

Also reports, for every reachable free/decoded cell of the chain, WHICH RULE FIRED AT THE TOP -- that
map is the case analysis the Lean `law` proof has to follow.
"""
import sys, random, collections
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, trace as tr
from freemodel import size, rand_term
import importlib.util
spec = importlib.util.spec_from_file_location('_rep12', D + '/gen/_x23357_rep.py')
m = importlib.util.module_from_spec(spec)
argv = list(sys.argv); sys.argv = [sys.argv[0]]
spec.loader.exec_module(m)
law, rules = m.law, m.rules
TAGS = [r[2] for r in rules]
show = tr.show
J = lambda a, b: ('J', a, b)


class CT(cf.Closed):
    """records which rule produced each pair, so the top product's rule is readable"""
    def __init__(self, law, rules):
        super().__init__(law, rules); self.ruleof = {}

    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key)
        res = None
        for i, (conds, x, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(x, u, v)
                if r is not None:
                    res = r; self.fired[i] = self.fired.get(i, 0) + 1
                    self.ruleof[key] = i; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        self.memo[key] = res
        return res


def mk(C, rng, small, junk, fam, lvl):
    """return (x, y, z) for family `fam` at nesting level `lvl`"""
    S = lambda: rng.choice(small)
    Jk = lambda: rng.choice(junk)
    encU = lambda X, Y: C.op(C.op(Y, X), Y)
    encV = lambda X, Y, Z: C.op(X, C.op(Y, Z))
    if fam == 'rand':
        return S(), S(), Jk()
    if fam == 'coincide':
        t = S(); return rng.choice([(t, t, Jk()), (t, S(), t), (S(), t, t), (t, t, t)])
    if fam == 'encA':                      # force A = op y x to decode
        j = S(); Y = S()
        for _ in range(lvl): j = encV(j, Y, Jk())
        return encV(j, Y, Jk()), encU(j, Y), Jk()
    if fam == 'encB':                      # force B = op y z to decode
        j = S(); Y = S()
        for _ in range(lvl): j = encV(j, Y, Jk())
        return S(), encU(j, Y), encV(j, Y, Jk())
    if fam == 'encV':                      # force V = op x B to decode: x is a u-side, B a v-side
        j = S(); Y = S()
        for _ in range(lvl): j = encU(j, Y)
        return encU(j, Y), j, C.op(Y, Jk())
    if fam == 'H3y_V':                     # y is an encoding whose DECODER is x
        j = S(); w = Jk(); x = S()
        for _ in range(lvl): j = encV(j, x, Jk())
        return x, encV(j, x, w), Jk()
    if fam == 'H3y_U':                     # y is the u-side encoding read BY x
        j = S(); x = S()
        for _ in range(lvl): j = encU(j, x)
        return x, encU(j, x), Jk()
    if fam == 'H3z':                       # z is an encoding by x
        j = S(); x = S()
        for _ in range(lvl): j = encV(j, x, Jk())
        return x, S(), encV(j, x, Jk())
    if fam == 'H3x':                       # x is an encoding by the law's own y
        j = S(); y = S()
        for _ in range(lvl): j = encV(j, y, Jk())
        return encV(j, y, Jk()), y, Jk()
    if fam == 'H3xu':                      # x is the u-side encoding read by the law's own y
        j = S(); y = S()
        for _ in range(lvl): j = encU(j, y)
        return encU(j, y), y, Jk()
    raise ValueError(fam)


FAMS = ['rand', 'coincide', 'encA', 'encB', 'encV', 'H3y_V', 'H3y_U', 'H3z', 'H3x', 'H3xu']

if __name__ == '__main__':
    N = int(argv[1]) if len(argv) > 1 else 300
    LV = [0, 1, 2, 3]
    grand = collections.Counter(); topmap = collections.defaultdict(collections.Counter)
    totbad = 0; worst = None
    for fam in FAMS:
        for lvl in LV:
            fired = collections.Counter(); hits = 0; bad = 0
            cells = collections.Counter()
            for sd in (5, 19):
                rng = random.Random(sd)
                C = CT(law, rules)
                small = [rand_term(rng.randint(1, 3), 2) for _ in range(80)]
                junk = [rand_term(rng.randint(5, 9), 3) for _ in range(80)]
                for _ in range(N):
                    try:
                        x, y, z = mk(C, rng, small, junk, fam, lvl)
                        if max(size(t) for t in (x, y, z)) > 500: continue
                        before = dict(C.fired)
                        A = C.op(y, x); U = C.op(A, y); B = C.op(y, z); V = C.op(x, B)
                        top = C.op(U, V)
                    except (RecursionError, KeyError):
                        continue
                    hits += 1
                    for k in set(list(C.fired) + list(before)):
                        fired[k] += C.fired.get(k, 0) - before.get(k, 0)
                    cell = (('AD' if A != J(y, x) else 'AF'), ('UD' if U != J(A, y) else 'UF'),
                            ('BD' if B != J(y, z) else 'BF'), ('VD' if V != J(x, B) else 'VF'))
                    cells[cell] += 1
                    ri = C.ruleof.get((U, V))
                    topmap[cell][TAGS[ri] if ri is not None else 'FREE'] += 1
                    grand[cell] += 1
                    if top != x:
                        bad += 1; totbad += 1
                        t = size(x) + size(y) + size(z)
                        if worst is None or t < worst[0]: worst = (t, fam, lvl, x, y, z)
            ctl = ' '.join('%s=%d' % (TAGS[k], fired.get(k, 0)) for k in range(len(rules)))
            miss = [TAGS[k] for k in range(len(rules)) if fired.get(k, 0) == 0]
            print('%-8s lvl=%d hits=%-5d BAD=%d | %s%s' % (fam, lvl, hits, bad, ctl,
                  ('   VACUOUS-FOR: ' + ','.join(miss)) if miss else ''), flush=True)
    print('\nTOTAL BAD', totbad, flush=True)
    if worst:
        t, fam, lvl, x, y, z = worst
        print('SMALLEST BAD fam=%s lvl=%d  x=%s  y=%s  z=%s' % (fam, lvl, show(x)[:200], show(y)[:200], show(z)[:200]), flush=True)
    print('\n=== which rule fires AT THE TOP, per chain cell (this is the Lean case analysis) ===', flush=True)
    for cell, c in sorted(grand.items(), key=lambda kv: -kv[1]):
        print('  %-24s %-7d  %s' % (str(cell), c, dict(topmap[cell])), flush=True)
