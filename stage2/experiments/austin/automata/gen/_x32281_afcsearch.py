import random, sys
sys.path.insert(0, 'stage2/experiments/austin/automata/gen')
import _x32281_leanmirror as m
G=[m.G(i) for i in range(8)]
rng=random.Random(12345)
def mk(d):
    return rng.choice(G) if d<=0 or rng.random()<.32 else m.J(mk(d-1),mk(d-1))
def enc(u,p,w): return m.J(m.J(u,m.J(m.J(p,w),w)),w)
def openc(u,p,w): return m.J(m.op(u,m.op(m.op(p,w),w)),w)
cond=adec=0
for i in range(100000):
    x,y,z=mk(3),mk(3),mk(3)
    if i%3==0:
        w=mk(2); x=mk(2); y=enc(x,x,w)
    elif i%3==1:
        w=mk(2); x=mk(2); y=openc(mk(1),x,w)
    try: P=m.op(x,y); Q=m.op(P,y); A=m.op(z,Q)
    except RecursionError: continue
    if P==m.J(x,y): continue
    C=m.op(m.op(P,m.a2(y)),m.a2(y))
    if m.a1(y)==m.op(x,C) and m.op(x,C)!=m.J(x,C):
        cond+=1
        if A!=m.J(z,Q):
            adec+=1
            print('BAD',i,'sizes',*[m.sz(t) for t in (x,y,z,P,Q,A,C)])
            print('x=',x); print('y=',y); print('z=',z); print('C=',C)
            break
print('cond',cond,'bad',adec)
if cond == 0:
    raise SystemExit('AFc positive control absent: this run supplies no evidence')
