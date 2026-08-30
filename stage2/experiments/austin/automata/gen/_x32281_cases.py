"""Which of the four chain products decode, on adversarial instances?  Law 32281 (dualised):
   x = Y * ((Y * ((x*Z)*Z)) * Z)      [dict names: Y='z', Z='y']
   s1 = x*Z ; s2 = s1*Z ; s3 = Y*s2 ; s4 = s3*Z ; top = Y*s4
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
import closedform as cf, fuzz as fz
from freemodel import size, rand_term

rules = gen_rules()
C = cf.Closed(LAW, rules)

def isfree(r, a, b):
    return r[0] == 'J' and r[1] == a and r[2] == b

def classify(x, Y, Z):
    try:
        s1 = C.op(x, Z); s2 = C.op(s1, Z); s3 = C.op(Y, s2); s4 = C.op(s3, Z); top = C.op(Y, s4)
    except RecursionError:
        return None, None
    pat = ''.join('F' if isfree(r, a, b) else 'D'
                  for r, a, b in ((s1, x, Z), (s2, s1, Z), (s3, Y, s2), (s4, s3, Z)))
    return pat, (top == x)

# adversarial pool: closure fuzz style
random.seed(11)
cnt = collections.Counter(); bad = collections.Counter(); examples = {}
pool = [('g', i) for i in range(4)]
for it in range(2500):
    x = random.choice(pool); Y = random.choice(pool); Z = random.choice(pool)
    pat, ok = classify(x, Y, Z)
    if pat is None:
        continue
    cnt[pat] += 1
    if not ok:
        bad[pat] += 1
        examples.setdefault(pat, (x, Y, Z))
    # grow the pool with the products we just built
    if len(pool) < 400 and it % 1 == 0:
        try:
            s1 = C.op(x, Z); s2 = C.op(s1, Z); s3 = C.op(Y, s2); s4 = C.op(s3, Z)
            for t in (s1, s2, s3, s4, C.op(Y, s4)):
                if size(t) <= 60:
                    pool.append(t)
        except RecursionError:
            pass

for p in sorted(cnt, key=lambda p: -cnt[p]):
    print('%-6s total %5d  FAIL %5d' % (p, cnt[p], bad[p]))

def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(' + sh(t[1]) + '*' + sh(t[2]) + ')'
print()
for p, (x, Y, Z) in examples.items():
    print(p, 'x=', sh(x), ' Y=', sh(Y), ' Z=', sh(Z))
