"""Shared term utilities + the research set + duality map."""
import json, itertools
ROOT='c:/Users/nacho/Documents/GitHub/magma-ai'
def parse_term(s):
    s=s.strip(); depth=0
    for i,c in enumerate(s):
        if c=='(': depth+=1
        elif c==')': depth-=1
        elif c in '*◇' and depth==0: return (parse_term(s[:i]), parse_term(s[i+1:]))
    if s[0]=='(' and s[-1]==')': return parse_term(s[1:-1])
    return s
def parse_eq(s):
    l,r=s.split('='); return parse_term(l),parse_term(r)
def show(t): return t if isinstance(t,str) else '('+show(t[0])+' * '+show(t[1])+')'
def show_eq(e):
    l,r=e
    f=lambda t: t if isinstance(t,str) else show(t)[1:-1]
    return f(l)+' = '+f(r)
def dual(t): return t if isinstance(t,str) else (dual(t[1]),dual(t[0]))
VARS='xyzwuv'
def canon(e):
    """ETP canonical: variables renamed in order of first occurrence (lhs then rhs), orientation chosen as the one that appears in the catalog (we try both)."""
    outs=[]
    for l,r in ((e[0],e[1]),(e[1],e[0])):
        m={}
        def ren(t):
            if isinstance(t,str):
                if t not in m: m[t]=VARS[len(m)]
                return m[t]
            return (ren(t[0]),ren(t[1]))
        outs.append((ren(l),ren(r)))
    return outs
def load_catalog():
    cat={}
    for i,line in enumerate(open(ROOT+'/vendor/stage2-official/examples/problems/eq_size5.txt',encoding='utf-8'),1):
        line=line.strip()
        if line: cat[show_eq(parse_eq(line))]=i
    return cat
def load_rows():
    return [json.loads(l) for l in open(ROOT+'/data/hf_cache/research_order5_hard.jsonl',encoding='utf-8')]
def dual_id(eqstr,cat):
    e=parse_eq(eqstr); d=(dual(e[0]),dual(e[1]))
    for c in canon(d):
        k=show_eq(c)
        if k in cat: return cat[k]
    return None
if __name__=='__main__':
    cat=load_catalog(); rows=load_rows()
    hyps={r['eq1_id']:r['equation1'] for r in rows}; goals={r['eq2_id']:r['equation2'] for r in rows}
    # sanity: catalog id of each equation string
    for k,v in list(hyps.items())[:3]:
        for c in canon(parse_eq(v)):
            if show_eq(c) in cat: print('check',k,cat[show_eq(c)])
    dh={k:dual_id(v,cat) for k,v in hyps.items()}; dg={k:dual_id(v,cat) for k,v in goals.items()}
    print('GOAL duals:',dg)
    inset=set(hyps)
    pairs=set()
    for k,d in dh.items():
        if d is not None and str(d) in inset: pairs.add(tuple(sorted((int(k),d))))
    print('hyp dual pairs both in set:',len(pairs),sorted(pairs))
    print('hyps whose dual is not in set:',sorted(int(k) for k,d in dh.items() if str(d) not in inset))
    # rows up to duality
    rowkeys=set()
    for r in rows:
        a=(int(r['eq1_id']),int(r['eq2_id'])); b=(dh[r['eq1_id']],dg[r['eq2_id']])
        rowkeys.add(min(a,b))
    print('distinct rows up to duality:',len(rowkeys))
    # hypotheses up to duality
    hk=set(min(int(k),d) for k,d in dh.items())
    print('distinct hyps up to duality:',len(hk))
    json.dump({'hyp_dual':dh,'goal_dual':dg},open('duals.json','w'))
