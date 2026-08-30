"""23357: candidate MINIMAL rule sets, modelled on the accepted 23354 certificate.

23354  x = ((y*x)*y)*(x*(x*z))   ships with FOUR rules and the structure
    Rfree : op (op y x) y = J (op y x) y          -- the u-side is always free
    ONESIDE : no term is both the right arg and the left arg of a decoding pair
    law   : case on `op y x` free/decoded and `op x z` free/decoded; the 4th cell is ONESIDE.
23357  x = ((y*x)*y)*(x*(y*z))   has the SAME left half, so Rfree should transfer.

Chain: A = op y x ; U = op A y ; B = op y z ; V = op x B ; top = op U V = x.
With U = J A y (Rfree):  y = a2 U,  A = a1 U.
  R*  : tg u=2, tg v=2, op (a2 u) (a1 v) = a1 u  ->  a1 v      (covers V free, A free or decoded)
  RD  : Ushape, tg x=2, op (a2 x) v = a1 x       ->  x         (V = R-decode of (x,B))
  LD  : Ushape, x = J (J p q) p, v = q           ->  x         (V = L-decode of (x,B))
where Ushape = tg u=2 & tg (a1 u)=2 & a1(a1 u)=a2 u, x = a2 (a1 u), y = a1 (a1 u) = a2 u.
"""
import sys, os, time, collections
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, revalidate as rv
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 23357
law = normalise(parse_eq(catalog()[EQ]))

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e)
A2 = lambda e: ('A2', e)
TG = lambda e: ('TG', e)
EQ_ = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b)
OP = lambda a, b: ('OP', a, b)

u1 = A1(U); u11 = A1(u1); u12 = A2(u1); u2 = A2(U)
TOP = [TG(U), TG(u1), EQ_(u11, u2)]
X = u12                      # x
Y = u11                      # y

RSTAR = ([TG(U), TG(V), OPEQ(OP(u2, A1(V)), u1)], A1(V), 'R*')
RD    = (TOP + [TG(X), OPEQ(OP(A2(X), V), A1(X))], X, 'RD')
LD    = (TOP + [TG(X), TG(A1(X)), EQ_(A1(A1(X)), A2(X)), EQ_(V, A2(A1(X)))], X, 'LD')
# free reading, fully structural (the N rule of 23354)
NFREE = (TOP + [TG(V), EQ_(X, A1(V)), TG(A2(V)), EQ_(Y, A1(A2(V)))], X, 'N')
# R* restricted to the shape where v is free: same guard plus tg (a2 v)=2
RSTAR2 = ([TG(U), TG(V), TG(A2(V)), OPEQ(OP(u2, A1(V)), u1)], A1(V), 'R*2')
# the As rule (recompute u from v): 23357's P12
AS = ([TG(V), TG(A2(V)), OPEQ(OP(OP(A1(A2(V)), A1(V)), A1(A2(V))), U)], A1(V), 'As')

SETS = {
    's3':   [LD, RD, RSTAR],
    's3b':  [RD, LD, RSTAR],
    's4':   [NFREE, LD, RD, RSTAR],
    's2':   [LD, RSTAR],
    's3as': [LD, RD, AS],
    's4as': [NFREE, LD, RD, AS],
    's3r2': [LD, RD, RSTAR2],
    'sRD':  [RD, RSTAR],
    'sLD':  [LD, RSTAR],
    'sR':   [RSTAR],
}

if __name__ == '__main__':
    for name in (sys.argv[1:] or ['s3', 's3b', 's4', 's2', 's3as', 's4as', 's3r2', 'sRD', 'sLD', 'sR']):
        rules = SETS[name]
        t0 = time.time()
        f = [q for q in rv.run_tests(law, rules, [3, 4, 5], 3000, 12000) if q[1] != 'recursion']
        k = collections.Counter(q[2] for q in f)
        print('%-7s %d rules  run_tests fails %d %s (%.0fs)' % (name, len(rules), len(f), dict(k), time.time() - t0), flush=True)
        if f:
            print('    first:', {a: b for a, b in f[0][0].items()}, flush=True)
