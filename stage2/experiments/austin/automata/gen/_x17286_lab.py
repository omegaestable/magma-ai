"""Law 17286 model laboratory -- the RECURSIVE-DECODER carrier.

Law (L-form):  x = (y*x) * (z*(z*(x*z)))
Chain:  A = op(y,x) ; P = op(x,z) ; Q = op(z,P) ; B = op(z,Q) ; goal op(A,B) = x.

The extractor's free model reads the payload at a FIXED accessor depth, and level k of the
encoding tower puts it at depth 3k+2 -- so no finite rule set works (see NOTES_17286.md).
Here `op` UNWRAPS the code as many times as needed instead:

  op u v =  if  v is a two-level code (tg v = 2, tg (a2 v) = 2, a1 v = a1 (a2 v))  then
               let w = a1 v, P = a2 (a2 v)
               search c down the unwrap chain of P for the first c with
                   op c w = P          (c really is what produced P against w)
               and return it
            else J u v

`u` enters only through the free case c = a2 u, which the same test covers.
Termination: the unwrap step  c := a1 (a2 (a2 c))  is a PROPER SUBTERM (structural), so it does
not rely on `sz (op a b) < sz b`, which is FALSE for this model (the RS refutation).
"""
import sys, itertools

def tg(t): return 1 if t[0] == 'g' else 2
def a1(t): return t[1] if t[0] != 'g' else t
def a2(t): return t[2] if t[0] != 'g' else t
def sz(t): return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1
g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
def show(t, cap=34):
    if sz(t) > cap: return '<sz%d>' % sz(t)
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1], 9999), show(t[2], 9999))
def encB(p, w): return J(w, J(w, J(p, w)))

MAXD = 400

class Mod:
    """v4: the candidate search SPLIT into two branches so every recursive call descends
    unconditionally under  sz u + sz v  (no reliance on short-circuit evaluation):

      branch U : c = a2 u              check  op (a2 u) (a1 v) = P        -- both args shrink
      branch V : c in [a1 P] ++ unwraps(P)   check  codes u c  AND  op c (a1 v) = P
                 -- here c is inside v, so `codes u c`'s call  op u (a1 c)  has a1 c inside v,
                 -- and  op c (a1 v)  has  sz c + sz (a1 v) < sz v  (since sz v = 2*sz w + sz P + 2)

    `codes` is therefore NEVER called with c = a2 u, which was the one call that could grow the
    measure.  Shared memo across the whole sweep (op is a pure function of (u,v)); `cycles` must
    stay 0 or the memo could be poisoned by the in-progress fallback.
    """
    def __init__(self):
        self.memo = {}; self.inprog = set(); self.cycles = 0; self.depth = 0
        self.fired = {}
    def unwraps(self, P):
        out = []; cur = P; n = 0
        while tg(cur) == 2 and tg(a2(cur)) == 2 and a1(cur) == a1(a2(cur))               and tg(a2(a2(cur))) == 2 and n < 40:
            c = a1(a2(a2(cur))); out.append(c); cur = c; n += 1
        return out
    def codes(self, u, c):
        if tg(c) != 2 or tg(a2(c)) != 2: return False
        if a1(c) != a1(a2(c)): return False
        return self.op(u, a1(c)) == a2(a2(c))
    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return J(u, v)
        if self.depth > MAXD: return J(u, v)
        self.inprog.add(key); self.depth += 1
        res = None; tag = None
        if tg(v) == 2 and tg(a2(v)) == 2 and a1(v) == a1(a2(v)):
            w = a1(v); P = a2(a2(v))
            # branch U -- u free, payload a2 u.   op (a2 u) w : a2 u < u, w < v  -> decreases
            if tg(u) == 2 and self.op(a2(u), w) == P:
                res = a2(u); tag = 'U'
            # branch R -- RECONSTRUCTION  c = J (a1 P) P.  `op c w = P` is exactly branch U at (c,w),
            # so INLINE it: that replaces the call on the constructed c (whose size is not bounded by
            # v) with  op P (a1 w)  --  P < v and a1 w < v, both strictly inside v.
            elif (tg(P) == 2 and tg(w) == 2 and tg(a2(w)) == 2 and a1(w) == a1(a2(w))
                  and self.op(u, a1(P)) == a2(P)            # codes u (J (a1 P) P)
                  and self.op(P, a1(w)) == a2(a2(w))):      # op (J (a1 P) P) w = P, via branch U
                res = J(a1(P), P); tag = 'R'
            else:
                # branch V -- payload located inside v (projection or unwrap); c is a subterm of v,
                # so  sz c + sz w < sz v  and  op c w  decreases.
                cs = ([a1(P)] if tg(P) == 2 else []) + self.unwraps(P)
                seen = set()
                for i, c in enumerate(cs):
                    if c in seen: continue
                    seen.add(c)
                    if self.codes(u, c) and self.op(c, w) == P:
                        res = c; tag = 'V%d' % i; break
        self.depth -= 1; self.inprog.discard(key)
        if res is None: res = J(u, v); tag = 'F'
        self.fired[tag] = self.fired.get(tag, 0) + 1
        self.memo[key] = res
        return res

def chain(M, x, y, z):
    A = M.op(y, x); P = M.op(x, z); Q = M.op(z, P); B = M.op(z, Q); top = M.op(A, B)
    return top, (A, P, Q, B)

def terms(maxsz, gens):
    out = {1: [g(i) for i in range(gens)]}
    for n in range(2, maxsz + 1):
        cur = []
        for a in range(1, n):
            b = n - 1 - a
            if b < 1: continue
            for t1 in out.get(a, ()):
                for t2 in out.get(b, ()): cur.append(J(t1, t2))
        out[n] = cur
    return [t for n in sorted(out) for t in out[n]]

def deep(n, a=2, b=3):
    t = g(a)
    for i in range(n): t = J(t, g(b))
    return t

def tower(base, ws):
    ts = [base]
    for w in ws: ts.append(encB(ts[-1], w))
    return ts

SH = Mod()

if __name__ == '__main__':
    print('== level-k descent (the oracle that caught the free model) ==')
    for lvl in range(0, 4):
        for jname, junk in (('small', g(9)), ('big', deep(13))):
            ws = [g(20 + i) for i in range(lvl + 2)]
            bad = 0; n = 0; cyc = 0; ex = None
            for seed, base in ((1, g(0)), (2, J(g(0), g(1)))):
                ts = tower(base, ws)
                cands = []
                for k, t in enumerate(ts):
                    cands.append(t); cands.append(J(junk, t))
                    if t[0] == 'J': cands += [t[1], t[2]]
                cands = [c for c in cands if sz(c) <= 400][:14]
                for x in cands:
                    for y in cands:
                        for z in cands:
                            if sz(x) + sz(y) + sz(z) > 700: continue
                            if n > 4000: break
                            try: top, _ = chain(SH, x, y, z)
                            except RecursionError: continue
                            n += 1
                            if top != x:
                                bad += 1
                                if ex is None: ex = (x, y, z, top)
            print('  lvl %d %-6s tested %-6d bad %-5d cycles %d  cells %s' % (lvl, jname, n, bad, SH.cycles, dict(sorted(SH.fired.items()))))
            if ex and bad:
                print('     e.g. x=%s y=%s z=%s -> %s' % (show(ex[0]), show(ex[1]), show(ex[2]), show(ex[3])))
    print('== exhaustive small terms ==')
    for mx, gn in ((7, 2), (9, 1)):
        T = terms(mx, gn); bad = 0; n = 0
        for x in T:
            for y in T:
                for z in T:
                    if sz(x) + sz(y) + sz(z) > 15: continue
                    try: top, _ = chain(SH, x, y, z)
                    except RecursionError: continue
                    n += 1
                    if top != x: bad += 1
        print('  sz<=%d/%dgen : %d triples, %d bad' % (mx, gn, n, bad))

# ---------------------------------------------------------------- full oracle stack
def evp(M, p, s):
    if isinstance(p, str): return s[p]
    return M.op(evp(M, p[0], s), evp(M, p[1], s))

def deep_and_coincidence(seeds=(1,2,3,4,5), N=20000, cap=90):
    """deep random + coincidence: the pool is fed the model's OWN chain values, but size-capped so
    the sampler does not drown in giant terms (the old version kept 354 of 100,000 draws)."""
    import random
    LAWP = (('y','x'), ('z',('z',('x','z'))))
    tot=0; bad=[]; branch={}
    for sd in seeds:
        random.seed(sd)
        pool=[g(0),g(1),g(2),J(g(0),g(1))]
        for i in range(N):
            def rnd(d):
                if d==0 or random.random()<0.45: return random.choice(pool)
                a=rnd(d-1); b=rnd(d-1)
                return J(a,b) if sz(a)+sz(b)<cap else random.choice(pool)
            s={'x':rnd(2),'y':rnd(2),'z':rnd(2)}
            r=random.random()
            if r<0.35: s['z']=encB(random.choice(pool),random.choice(pool))
            elif r<0.55: s['x']=encB(random.choice(pool),random.choice(pool))
            if random.random()<0.25: s['y']=J(deep(9),random.choice(pool))
            if max(sz(t) for t in s.values())>cap: continue
            before=dict(SH.fired)
            try: r2=evp(SH,LAWP,s)
            except RecursionError: continue
            tot+=1
            for k in SH.fired:
                d=SH.fired[k]-before.get(k,0)
                if d: branch[k]=branch.get(k,0)+d
            if r2!=s['x']: bad.append((sd,s,r2))
            for t in (SH.op(s['x'],s['z']), encB(s['x'],s['z'])):
                if sz(t)<=cap and len(pool)<250: pool.append(t)
    return tot,bad,branch

def forced_firing():
    """the tenth rung: for each branch, satisfy its precondition and place that term at EVERY
    product of the law's chain, not only the one it was derived for."""
    PROD=['A=op(y,x)','P=op(x,z)','Q=op(z,P)','B=op(z,Q)','top=op(A,B)']
    # terms that force each branch when used as the RIGHT argument
    payloads=[g(0), J(g(0),g(1)), encB(g(0),g(1))]
    forcers=[]
    for p in payloads:
        for w in (g(5), J(g(5),g(6))):
            forcers.append(('U/V0', encB(p,w)))                    # one-level code
            forcers.append(('V1',  encB(encB(p,w), g(7))))         # two-level code -> needs an unwrap
    lefts=[J(g(9),p) for p in payloads] + [J(deep(9),p) for p in payloads] + payloads
    mat={}; bad=[]; n=0
    cands=[t for _,t in forcers]+lefts
    for x in cands:
        for y in cands:
            for z in cands:
                if sz(x)+sz(y)+sz(z)>260: continue
                before=dict(SH.fired)
                try:
                    A=SH.op(y,x); P=SH.op(x,z); Q=SH.op(z,P); B=SH.op(z,Q); top=SH.op(A,B)
                except RecursionError: continue
                n+=1
                if top!=x: bad.append((x,y,z,top))
                for k,(a,b) in enumerate([(y,x),(x,z),(z,P),(z,Q),(A,B)]):
                    key=SH.memo.get((a,b))
                    tag='F' if key==J(a,b) else 'D'
                    mat[(tag,k)]=mat.get((tag,k),0)+1
    return n,bad,mat,PROD

if __name__ == '__main__' and '--full' in sys.argv:
    print('== deep + coincidence (model-built pool, size-capped) ==')
    tot,bad,branch = deep_and_coincidence()
    print('  %d chains, %d bad ; branches %s'%(tot,len(bad),dict(sorted(branch.items()))))
    for sd,s2,r in bad[:4]:
        print('   seed%d x=%s y=%s z=%s -> %s'%(sd,show(s2['x']),show(s2['y']),show(s2['z']),show(r)))
    print('== forced firing (each branch placed at every chain product) ==')
    n,bad2,mat,PROD = forced_firing()
    print('  %d triples, %d bad'%(n,len(bad2)))
    for x,y,z,top in bad2[:4]:
        print('   x=%s y=%s z=%s -> %s'%(show(x),show(y),show(z),show(top)))
    print('  decoded/free per chain product:')
    for k,pn in enumerate(PROD):
        print('     %-12s decoded %-6d free %-6d'%(pn,mat.get(('D',k),0),mat.get(('F',k),0)))
