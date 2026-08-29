import sys, random, time
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
import fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq
import freetest2 as ft

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
rules = [([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A1', ('A1', ('A1', ('V',))))), ('TG', ('A2', ('V',))), ('EQ', ('A2', ('A1', ('A1', ('V',)))), ('A1', ('A2', ('V',)))), ('EQ', ('A2', ('A1', ('V',))), ('A2', ('A2', ('V',))))], ('A2', ('A1', ('A1', ('V',)))), 'free'),
 ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A1', ('A1', ('A1', ('V',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('V',)))), ('A2', ('A1', ('V',)))), ('A2', ('V',)))], ('A2', ('A1', ('A1', ('V',)))), 'B1l'),
 ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('OPEQ', ('OP', ('OP', ('U',), ('A1', ('A2', ('V',)))), ('A2', ('A2', ('V',)))), ('A1', ('V',)))], ('A1', ('A2', ('V',))), 'B0l'),
 ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A2', ('A1', ('V',)))), ('TG', ('A1', ('A2', ('A1', ('V',))))), ('TG', ('A1', ('A1', ('A2', ('A1', ('V',)))))), ('OPEQ', ('OP', ('A1', ('A1', ('A1', ('A2', ('A1', ('V',)))))), ('A2', ('A1', ('V',)))), ('A2', ('V',))), ('OPEQ', ('OP', ('U',), ('A1', ('A1', ('A1', ('A2', ('A1', ('V',))))))), ('A1', ('A1', ('V',))))], ('A1', ('A1', ('A1', ('A2', ('A1', ('V',)))))), 'B00l,B1l')]

A_pat, B_pat = law[1]  # A_pat = 'y', B_pat = ((('y','x'),'z'),('x','z'))
A2_pat, B2_pat = B_pat  # A2_pat = (('y','x'),'z'), B2_pat = ('x','z')

class CheckC(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules)
        self.vfree_bad = []
    def evp(self, p, s):
        if isinstance(p, str): return s[p]
        r = self.op(self.evp(p[0], s), self.evp(p[1], s))
        if p == B_pat:
            N2 = self.evp(A2_pat, s)
            N3 = self.evp(B2_pat, s)
            if r != ('J', N2, N3):
                self.vfree_bad.append((dict(s), N2, N3, r))
        return r

C = CheckC(law, rules)
t0 = time.time()
tested, fails = cf.deep_tests(C, law, 8000, 200, 12087*7+99)
print('deep', tested, 'fails', len(fails), 'vfree_bad', len(C.vfree_bad), time.time()-t0)
tested2, fails2 = fz.fuzz(C, law, rules, 8000, seed=12087+500)
print('fuzz', tested2, 'fails', len(fails2), 'vfree_bad total', len(C.vfree_bad), time.time()-t0)
tested3, fails3 = fz.closure_fuzz(C, law, 8000, seed=12087+700)
print('closure', tested3, 'fails', len(fails3), 'vfree_bad total', len(C.vfree_bad), time.time()-t0)
tested4, fails4 = fz.critical_fuzz(C, law, 8000, seed=12087+900)
print('critical', tested4, 'fails', len(fails4), 'vfree_bad total', len(C.vfree_bad), time.time()-t0)
for b in C.vfree_bad[:5]:
    print('VFREE-BAD', b)
