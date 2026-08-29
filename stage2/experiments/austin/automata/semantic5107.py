"""Semantic fixed-point model for 5107: x = y*(y*(y*(z*(x*y)))).
op(u,v) = x if exists x,z (subterms of u,v): v == chain(u,z,x) := op(u,op(u,op(z,op(x,u))))  else J(u,v)."""
import random, sys, functools
sys.setrecursionlimit(10000)
def subterms(t, acc):
    acc.add(t)
    if t[0]=='J':
        subterms(t[1],acc); subterms(t[2],acc)
    return acc
memo={}
DEPTH=[0]; MAXD=60; bail=[0]
def op(u,v):
    key=(u,v)
    if key in memo: return memo[key]
    DEPTH[0]+=1
    if DEPTH[0]>MAXD:
        DEPTH[0]-=1; bail[0]+=1; return ('J',u,v)
    res=None
    cands=subterms(u,set())|subterms(v,set())
    for x in cands:
        for z in cands:
            c=op(x,u); c=op(z,c); c=op(u,c); c=op(u,c)
            if c==v:
                res=x; break
        if res is not None: break
    if res is None: res=('J',u,v)
    DEPTH[0]-=1
    memo[key]=res
    return res
def rand_term(d):
    if d<=0 or random.random()<0.3: return ('g',random.randrange(3))
    return ('J',rand_term(d-1),rand_term(d-1))
def law(x,y,z):
    return op(y,op(y,op(y,op(z,op(x,y)))))==x
random.seed(1); bad=0; N=int(sys.argv[1]) if len(sys.argv)>1 else 300
for i in range(N):
    x,y,z=rand_term(2),rand_term(2),rand_term(2)
    # bias: make y a chain built from x sometimes, or z=x
    r=random.random()
    if r<0.3: y=op(x,op(x,op(rand_term(2),op(rand_term(2),x))))
    elif r<0.5: z=x
    elif r<0.6: y=op(x,op(rand_term(2),op(rand_term(2),x)))
    if i%10==0: print("progress",i,"memo",len(memo),flush=True)
    if not law(x,y,z):
        bad+=1
        if bad<=3: print('FAIL x=',x,'y=',y,'z=',z)
print('tests',N,'bad',bad,'bailouts',bail[0],'memo',len(memo))
