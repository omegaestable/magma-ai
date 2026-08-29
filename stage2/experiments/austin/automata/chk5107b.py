import sys, random
sys.setrecursionlimit(100000)
exec(open('chk5107.py').read().split("maxsz=")[0])
random.seed(7)
def rt(d):
    if d<=0 or random.random()<0.3: return ('g',random.randrange(3))
    return ('J',rt(d-1),rt(d-1))
def chain(y,z,x): return op(y,op(y,op(z,op(x,y))))
bad=0; N=40000
for i in range(N):
    x,y,z=rt(3),rt(3),rt(3)
    r=random.random()
    if r<0.25: y=chain(x,rt(2),rt(2))
    elif r<0.4: z=x
    elif r<0.5: y=op(x,op(rt(2),op(rt(2),x)))
    elif r<0.6: y=J(x,J(x,J(rt(2),op(a1(x),x))))
    elif r<0.7: y=J(x,J(x,J(x,x))); z=y
    elif r<0.8:
        p=op(a1(x),x); y=J(x,J(x,op(a1(p),p)))
    elif r<0.9: y=x; z=x
    if op(y,op(y,op(y,op(z,op(x,y)))))!=x:
        bad+=1
        if bad<5: print("FAIL",x,y,z)
print("random tests",N,"bad",bad)
