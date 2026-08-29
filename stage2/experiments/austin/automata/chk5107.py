import sys, itertools, functools
sys.setrecursionlimit(100000)
# terms: ('g',n) or ('J',a,b)
def sz(t): return 1 if t[0]=='g' else sz(t[1])+sz(t[2])+1
def tg(t): return 1 if t[0]=='g' else 2
def a1(t): return t[1] if t[0]=='J' else t
def a2(t): return t[2] if t[0]=='J' else t
def G0(u,v): return tg(v)==2 and a1(v)==u and tg(a2(v))==2 and a1(a2(v))==u
@functools.lru_cache(maxsize=None)
def op(u,v):
    if not G0(u,v): return ('J',u,v)
    w=a2(a2(v))
    if tg(w)==2 and tg(a2(w))==2 and a2(a2(w))==u: return a1(a2(w))
    p=op(a1(u),u)
    if tg(w)==2 and a2(w)==p: return a1(u)
    if tg(u)==2 and tg(a2(u))==2 and tg(a2(a2(u)))==2 and a1(a2(a2(u)))==w and a2(a2(a2(u)))==a1(u): return a1(u)
    if sz(a1(p))+sz(p) < sz(u)+sz(v):
        if w==op(a1(p),p): return a1(u)
        return ('J',u,v)
    print("HS FAIL", u, v); return ('J',u,v)
def terms(n, gens):
    # all terms of size exactly n
    if n==1: return [('g',i) for i in range(gens)]
    out=[]
    for k in range(1,n-1):
        for a in terms(k,gens):
            for b in terms(n-1-k,gens):
                out.append(('J',a,b))
    return out
def J(a,b): return ('J',a,b)
maxsz=int(sys.argv[1]) if len(sys.argv)>1 else 7
gens=int(sys.argv[2]) if len(sys.argv)>2 else 2
T=[]
for n in range(1,maxsz+1): T+=terms(n,gens)
print("terms",len(T))
bad=0
for y in T:
    for x in T:
        for z in T:
            if op(y,op(y,op(y,op(z,op(x,y)))))!=x:
                bad+=1
                if bad<5: print("LAW FAIL x=",x,"y=",y,"z=",z)
print("law bad",bad)
# candidate lemmas
def check(name,f):
    b=0
    for u in T:
        for v in T:
            if not f(u,v):
                b+=1
                if b<3: print(name,"FAIL",u,v)
    print(name,"bad",b)
check("TR", lambda u,v: op(u,v)==J(u,v) or (G0(u,v) and (op(u,v)==a1(u) or sz(op(u,v))<sz(a2(a2(v))))))
check("R2", lambda u,v: op(u, J(u,J(u,J(v,op(a1(u),u)))))==a1(u))
def r4(u,v):
    p=op(a1(u),u); w=op(a1(p),p); return op(u,J(u,J(u,w)))==a1(u)
check("R4", lambda u,v: r4(u,v))
check("SELF", lambda u,v: op(u,J(u,J(u,u)))==J(u,J(u,J(u,u))))
check("PAYne", lambda u,v: op(a1(u),u)!=u)
# N3: op y (op z (op x y)) = J y (...)  for all x y z
b=0
for y in T:
    for x in T:
        for z in T:
            P=op(x,y); Q=op(z,P)
            if op(y,Q)!=J(y,Q): b+=1; print("N3 fail",x,y,z) if b<3 else None
            R=J(y,Q)
            if op(y,R)!=J(y,R): b+=1; print("N4 fail",x,y,z) if b<3 else None
print("N3/N4 bad",b)
# R3: u = J a (J z3 (J w a)) -> op u (J u (J u w)) = a
b=0
for a in T:
    for z3 in T:
        for w in T:
            u=J(a,J(z3,J(w,a)))
            if op(u,J(u,J(u,w)))!=a: b+=1; print("R3 fail",a,z3,w) if b<3 else None
print("R3 bad",b)
