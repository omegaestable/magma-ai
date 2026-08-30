"""Query the forced congruence of a law for SPECIFIC candidate identities, and report
'junk-forgetting' merges: classes whose SMALLEST member still has size >= minsz
(i.e. two big distinct free terms identified with each other, not with a small one).

python gen/_id_query.py <eq> [base] [gens] [rounds] [minsz]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _id_cong as C

def run(eq, base=3, gens=2, rounds=2, minsz=5, cap=18, growsrc=24, extra=()):
    from freemodel import normalise, catalog
    from laws import parse_eq
    law = normalise(parse_eq(catalog()[eq]))
    LHS, RHS = law
    print('law %d : %s' % (eq, catalog()[eq]))
    cc = C.CC()
    for e in extra: cc.add(e)
    pool = C.terms_upto(base, gens)
    seen = set(pool); allpool = list(pool)
    for rd in range(1, rounds + 1):
        n = 0
        for y in allpool:
            for x in allpool:
                for z in pool:
                    r = C.build(RHS, {'x': x, 'y': y, 'z': z})
                    cc.add(r); cc.add(x); cc.union(r, x); n += 1
        for e in extra: cc.add(e)
        cc.run()
        print('  round %d: %d instances, %d nodes' % (rd, n, len(cc.p)), flush=True)
        new = []
        src = allpool if len(allpool) <= growsrc else allpool[:growsrc]
        for y in src:
            for x in src:
                for z in pool:
                    r = C.build(RHS, {'x': x, 'y': y, 'z': z})
                    st = []
                    def walk(i, d=0):
                        if d > 3: return
                        t = C.NODES[i]
                        if t[0] == 'J':
                            st.append(t[1]); st.append(t[2]); walk(t[1], d+1); walk(t[2], d+1)
                    walk(r)
                    for c in st:
                        if c not in seen and C.SZ[c] <= cap:
                            seen.add(c); new.append(c)
        allpool = allpool + new
    cls = {}
    for i in list(cc.p):
        if C.SZ[i] <= cap:
            cls.setdefault(cc.find(i), []).append(i)
    out = []
    for k, v in cls.items():
        if len(v) < 2: continue
        v = sorted(v, key=lambda t: C.SZ[t])
        m = C.SZ[v[0]]
        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                if C.SZ[v[i]] == C.SZ[v[j]] == m:
                    out.append((m, v[i], v[j]))
    out.sort()
    print('  MINIMAL EQUAL-SIZE distinct terms identified (true junk-forgetting): %d' % len(out))
    for sz_, a, b in out[:25]:
        print('    [%d] %s  ==  %s' % (sz_, C.show(a), C.show(b)))
    return cc

if __name__ == '__main__':
    eq = int(sys.argv[1]); base = int(sys.argv[2]) if len(sys.argv)>2 else 3
    gens = int(sys.argv[3]) if len(sys.argv)>3 else 2
    rounds = int(sys.argv[4]) if len(sys.argv)>4 else 2
    minsz = int(sys.argv[5]) if len(sys.argv)>5 else 5
    run(eq, base, gens, rounds, minsz)
