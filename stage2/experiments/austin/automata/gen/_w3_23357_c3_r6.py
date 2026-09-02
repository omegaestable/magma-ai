"""Constructed 23357 guard family C3 (B decoded through the A0s/R6 rule).

For q,r arbitrary, force the R6 shape at (y,z):
    z = J q r,  y = J (op (a1 q) q) (a1 q).
Then op(y,z) = a1 z = q (provided the preceding guards do not steal it).
This is a different decoded-B route from C1 (which uses R1 and returns q's
payload).  We retain only x for which V=op(x,B) is free, making the target
cell (AF,UF,BD,VF) explicit in this run.
"""
import sys, random, collections, importlib.util
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf
from freemodel import size, rand_term
import trace as tr

G = D + '/gen/'
spec = importlib.util.spec_from_file_location('_x23357_rep', G + '_x23357_rep.py')
mod = importlib.util.module_from_spec(spec)
old = list(sys.argv); sys.argv = [sys.argv[0]]; spec.loader.exec_module(mod); sys.argv = old
law, rules = mod.law, mod.rules
J = lambda a,b: ('J',a,b)
g = lambda n: ('g',n)
C = cf.Closed(law, rules)
show = tr.show

rng = random.Random(23357)
qs = [rand_term(rng.randint(1,4), 3) for _ in range(130)]
qs = [q for q in qs if q[0] == 'J']
rs = [g(20+i) for i in range(10)] + [rand_term(rng.randint(1,4), 3) for _ in range(120)]
xs = [g(100+i) for i in range(30)] + [rand_term(rng.randint(1,4), 3) for _ in range(150)]
tested = 0; bad = 0; controls = 0; cells = collections.Counter(); worst = None
for q in qs:
  for r in rs[:40]:
    # Accessors are represented directly on terms: a1(J p q)=p, hence
    # y = J (op (a1 q) q) (a1 q), and z=J q r.
    aq = q[1]
    y = J(C.op(aq, q), aq)
    z = J(q, r)
    B = C.op(y,z)
    if B == J(y,z):
      continue
    for x in xs[:40]:
      A = C.op(y,x); U = C.op(A,y); V = C.op(x,B)
      if V == J(x,B):
        top = C.op(U,V); tested += 1
        cell = ('AD' if A != J(y,x) else 'AF', 'UD' if U != J(A,y) else 'UF',
                'BD', 'VF')
        cells[cell] += 1; controls += 1
        if top != x:
          bad += 1
          score = size(x)+size(y)+size(z)
          if worst is None or score < worst[0]: worst=(score,x,y,z,B,top)
print('constructed R6-family tested=%d BAD=%d controls=%d cells=%s' %
      (tested,bad,controls,dict(cells)), flush=True)
if worst:
  _,x,y,z,B,top=worst
  print('smallest bad x=%s y=%s z=%s B=%s got=%s' %
        tuple(show(t)[:300] for t in (x,y,z,B,top)), flush=True)
if controls == 0:
  raise SystemExit('C3 positive control failed: no V-free, B-decoded target cell')
if bad:
  raise SystemExit('C3 R6 family refutes full12')
