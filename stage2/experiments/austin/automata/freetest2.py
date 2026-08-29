"""Deeper adversarial tests of the semantic free model: nested encodings, cross-linked variables."""
import sys, os, json, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import freemodel as fm
from laws import parse_eq
def nested_triple(F, pool):
    vs = F.vars
    def pick():
        r = random.random()
        if r < 0.3 or not pool: return fm.rand_term(random.choice([1, 1, 2]))
        return random.choice(pool)
    s = {v: pick() for v in vs}
    subs = fm.all_subpatterns(F.rhs, [])
    for _ in range(random.choice([1, 1, 2, 2, 3])):
        p = random.choice(subs)
        s0 = {v: pick() for v in vs}
        for v in vs:
            if random.random() < 0.6: s0[v] = s[random.choice(vs)]
        tgt = random.choice(vs)
        try: s[tgt] = F.ev(p, s0)
        except Exception: pass
    if random.random() < 0.3:
        a, b = random.sample(vs, 2); s[a] = s[b]
    return s
if __name__ == '__main__':
    eq = int(sys.argv[1]); N = int(sys.argv[2]); secs = float(sys.argv[3])
    cat = fm.catalog(); law = fm.normalise(parse_eq(cat[eq])); F = fm.Free(law)
    random.seed(eq * 7 + 1); t0 = time.time(); pool = []; fails = 0; tested = 0; maxsz = 0
    while tested < N and time.time() - t0 < secs:
        s = nested_triple(F, pool)
        if max(fm.size(v) for v in s.values()) > 120: continue
        lhs = F.op(F.ev(F.A, s), F.ev(F.B, s)); tested += 1
        maxsz = max(maxsz, max(fm.size(v) for v in s.values()))
        for v in s.values():
            if fm.size(v) <= 40 and len(pool) < 400: pool.append(v)
        if lhs != s['x']:
            fails += 1
            if fails <= 2: print('FAIL', {k: fm.size(v) for k, v in s.items()}, flush=True)
    print(json.dumps(dict(eq=eq, tested=tested, fails=fails, conflicts=len(F.conflicts), cycles=F.cycles, rbail=F.rbail, rcycles=F.rcycles, tainted=F.tainted, spurious=F.spurious, unverified=F.unverified, bail=F.bail,
                          cuts=F.cuts, memo=len(F.memo), maxsz=maxsz, secs=round(time.time() - t0, 1))))
