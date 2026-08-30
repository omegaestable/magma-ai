"""Tightened structural necessary conditions for 23354 (see _x23354_struct.py).
RDrec(t) := tg(a2 t)=2 and ( AFx (a2 t) (a1 t)  or  (tg(a1 t)=2 and a1(a2 t)=a1(a1 t) and RDrec(a2 t)) )
RD(x)    := tg x=2 and ( (tg(a1 x)=2 and a1(a1 x)=a2 x) or RDrec(x) )
LD(x)    := L1 or L2 or L3   (as in _x23354_struct.py)
"""
import sys
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')

def tg(t): return 2 if t[0] == 'J' else 1
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def sz(t): return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

def AFx(t, p):
    return tg(t) == 2 and tg(a1(t)) == 2 and a1(a1(t)) == a2(t) and a2(a1(t)) == p
def RDrec(t):
    if tg(a2(t)) != 2: return False
    if AFx(a2(t), a1(t)): return True
    return tg(a1(t)) == 2 and a1(a2(t)) == a1(a1(t)) and RDrec(a2(t))
def RD(x):
    if tg(x) != 2: return False
    return (tg(a1(x)) == 2 and a1(a1(x)) == a2(x)) or RDrec(x)

def L1(x): return tg(x) == 2 and tg(a2(x)) == 2 and a1(x) == a1(a2(x))
def L2(x): return (tg(x) == 2 and tg(a1(x)) == 2 and tg(a1(a1(x))) == 2
                   and a2(x) == a2(a1(a1(x))) and a1(a1(a1(x))) == a2(a1(x)))
def L3(x): return (tg(x) == 2 and tg(a1(x)) == 2 and tg(a2(x)) == 2
                   and a1(a1(x)) == a1(a2(x)))
def LD(x): return L1(x) or L2(x) or L3(x)

MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 15
NG = int(sys.argv[2]) if len(sys.argv) > 2 else 2
terms = {1: [('g', i) for i in range(NG)]}
for n in range(3, MAX + 1, 2):
    acc = []
    for a in range(1, n - 1):
        b = n - 1 - a
        for t1 in terms.get(a, []):
            for t2 in terms.get(b, []):
                acc.append(('J', t1, t2))
    terms[n] = acc
allt = [t for n in sorted(terms) for t in terms[n]]
print('terms', len(allt))
nrd = nld = 0; both = []
for t in allt:
    r = RD(t); l = LD(t)
    nrd += r; nld += l
    if r and l and len(both) < 10: both.append(t)
print('RD*', nrd, 'LD*', nld, 'BOTH', len(both))
for t in both:
    print('   ', sh(t), '| base', tg(a1(t)) == 2 and a1(a1(t)) == a2(t), 'RDrec', RDrec(t),
          '| L1', L1(t), 'L2', L2(t), 'L3', L3(t))
