"""Ask a law's forced congruence about the JUNK SLOT: is the code C(x,y,z) independent of z?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _id_cong as C, _id_query as Q
from freemodel import normalise, catalog
from laws import parse_eq

def mk(t):
    if isinstance(t, str): return C.g('abcdefg'.index(t))
    return C.J(mk(t[0]), mk(t[1]))

def sub(pat, s):
    if isinstance(pat, str): return s[pat]
    return (sub(pat[0], s), sub(pat[1], s))

def main(eq, base=3, gens=4, rounds=2):
    law = normalise(parse_eq(catalog()[eq]))
    RHS = law[1]
    CODE = RHS[1] if not isinstance(RHS[1], str) else RHS[0]   # the non-y child of the root
    # both children, whichever mentions x
    cands = []
    for side in (RHS[0], RHS[1]):
        if isinstance(side, str): continue
        if 'z' in str(side):
            cands.append(side)
    pairs = []
    for cd in cands:
        for xs, ys in (('a', 'b'), ('a', 'a'), ('b', 'a')):
            l = mk(sub(cd, {'x': xs, 'y': ys, 'z': 'c'}))
            r = mk(sub(cd, {'x': xs, 'y': ys, 'z': 'd'}))
            pairs.append(('code x=%s y=%s : z-independent?' % (xs, ys), l, r))
    extra = [t for _, l, r in pairs for t in (l, r)]
    cc = Q.run(eq, base, gens, rounds, 99, extra=extra)
    print('  --- junk-slot (z) independence of the code ---')
    for name, l, r in pairs:
        ok = (l in cc.p and r in cc.p and cc.find(l) == cc.find(r))
        print('   %-38s %s     %s' % (name, 'DERIVED' if ok else '.', C.show(l)))

if __name__ == '__main__':
    main(int(sys.argv[1]),
         int(sys.argv[2]) if len(sys.argv) > 2 else 3,
         int(sys.argv[3]) if len(sys.argv) > 3 else 4,
         int(sys.argv[4]) if len(sys.argv) > 4 else 2)
