"""Find the identity a law FORCES between distinct free terms, by ground congruence closure.

Method (sound by construction; every merge is a genuine consequence of the law):
  * hash-cons ground terms over generators a,b,...
  * assert  RHS(x,y,z) ~ x  for every assignment from a pool
  * congruence-close (union-find + signature table)
  * report classes that contain two distinct SMALL terms -- those pairs are the derived identities.

Rounds: round 1 uses a small base pool; each later round adds terms discovered in the previous round
(in particular the "code" terms C(a,a,z), which is the y := T substitution of the hand derivations).

python gen/_id_cong.py <eq> [base_size] [gens] [rounds]
"""
import sys, os, itertools, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from freemodel import normalise, catalog
from laws import parse_eq

# ---------- hash-consed ground terms ----------
NODES = []          # id -> ('g',n) or ('J', i, j)
INTERN = {}
SZ = []

def g(n):
    k = ('g', n)
    i = INTERN.get(k)
    if i is None:
        i = len(NODES); NODES.append(k); INTERN[k] = i; SZ.append(1)
    return i

def J(a, b):
    k = ('J', a, b)
    i = INTERN.get(k)
    if i is None:
        i = len(NODES); NODES.append(k); INTERN[k] = i; SZ.append(SZ[a] + SZ[b] + 1)
    return i

def show(i, cap=200):
    if SZ[i] > cap: return '<sz %d>' % SZ[i]
    t = NODES[i]
    if t[0] == 'g': return 'abcdefg'[t[1]]
    return '(%s*%s)' % (show(t[1], cap), show(t[2], cap))

# ---------- union-find + congruence closure ----------
class CC:
    def __init__(self):
        self.p = {}
        self.sig = {}          # (find a, find b) -> class id
        self.parents = {}      # class id -> list of node ids that are J-nodes with that class as child
        self.pending = []

    def add(self, i):
        if i in self.p: return i
        self.p[i] = i
        t = NODES[i]
        if t[0] == 'J':
            self.add(t[1]); self.add(t[2])
            self.parents.setdefault(self.find(t[1]), []).append(i)
            self.parents.setdefault(self.find(t[2]), []).append(i)
            k = (self.find(t[1]), self.find(t[2]))
            j = self.sig.get(k)
            if j is None: self.sig[k] = i
            else: self.pending.append((i, j))
        return i

    def find(self, i):
        r = i
        while self.p[r] != r: r = self.p[r]
        while self.p[i] != r: self.p[i], i = r, self.p[i]
        return r

    def union(self, a, b):
        self.pending.append((a, b))

    def run(self):
        while self.pending:
            a, b = self.pending.pop()
            ra, rb = self.find(a), self.find(b)
            if ra == rb: continue
            # keep the smaller-size representative
            if SZ[ra] > SZ[rb] or (SZ[ra] == SZ[rb] and ra > rb): ra, rb = rb, ra
            self.p[rb] = ra
            pb = self.parents.pop(rb, [])
            self.parents.setdefault(ra, []).extend(pb)
            for i in pb:
                t = NODES[i]
                k = (self.find(t[1]), self.find(t[2]))
                j = self.sig.get(k)
                if j is None: self.sig[k] = i
                elif self.find(j) != self.find(i): self.pending.append((i, j))

def terms_upto(n, gens):
    by = {1: [g(i) for i in range(gens)]}
    out = list(by[1])
    for s in range(2, n + 1):
        cur = []
        for a in range(1, s):
            b = s - 1 - a
            if b >= 1:
                for u in by[a]:
                    for v in by[b]: cur.append(J(u, v))
        by[s] = cur; out += cur
    return out

ASSERTED = set()

def direct(a, b):
    return (a, b) in ASSERTED or (b, a) in ASSERTED


def build(pat, s):
    if isinstance(pat, str): return s[pat]
    return J(build(pat[0], s), build(pat[1], s))

def main(eq, base=2, gens=2, rounds=3, cap=16, growsrc=24):
    law = normalise(parse_eq(catalog()[eq]))
    LHS, RHS = law
    print('law %d : %s' % (eq, catalog()[eq]))
    cc = CC()
    pool = terms_upto(base, gens)
    seen = set(pool)
    allpool = list(pool)
    reported = set()
    for rd in range(1, rounds + 1):
        t0 = time.time(); n = 0
        for y in allpool:
            for x in allpool:
                for z in pool:
                    r = build(RHS, {'x': x, 'y': y, 'z': z})
                    cc.add(r); cc.add(x)
                    cc.union(r, x); ASSERTED.add((r, x))
                    n += 1
        cc.run()
        cls = {}
        for i in list(cc.p):
            if SZ[i] <= cap:
                cls.setdefault(cc.find(i), []).append(i)
        out = []
        for k, v in cls.items():
            if len(v) < 2: continue
            v = sorted(v, key=lambda t: SZ[t])
            for i in range(len(v)):
                for j in range(i + 1, len(v)):
                    a, b = v[i], v[j]
                    if direct(a, b): continue
                    key = (a, b)
                    if key in reported: continue
                    reported.add(key)
                    out.append((SZ[a] + SZ[b], a, b))
        out.sort()
        print('round %d: %d instances, %d nodes, %.1fs, %d NEW non-direct merges'
              % (rd, n, len(cc.p), time.time() - t0, len(out)), flush=True)
        for _, a, b in out[:15]:
            print('   %s   ==   %s' % (show(a), show(b)), flush=True)
        # grow the pool with every proper subterm of RHS(x,y,z) over the CURRENT pool
        new = []
        src = allpool if len(allpool) <= growsrc else allpool[:growsrc]
        for y in src:
            for x in src:
                for z in pool:
                    r = build(RHS, {'x': x, 'y': y, 'z': z})
                    st = []
                    def walk(i, d=0):
                        if d > 3: return
                        t = NODES[i]
                        if t[0] == 'J':
                            st.append(t[1]); st.append(t[2])
                            walk(t[1], d + 1); walk(t[2], d + 1)
                    walk(r)
                    for c in st:
                        if c not in seen and SZ[c] <= cap:
                            seen.add(c); new.append(c)
        allpool = allpool + new
        print('   pool -> %d' % len(allpool), flush=True)
    return []


if __name__ == '__main__':
    eq = int(sys.argv[1])
    base = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    gens = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    rounds = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    main(eq, base, gens, rounds)
