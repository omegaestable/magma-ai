"""Check T5B standalone coverage (independent of T4A)."""
import json

T4A = [[0,1,2],[2,0,1],[1,2,0]]
T5B = [[0,2,1],[1,0,2],[2,1,0]]
T3R = [[1,2,0],[1,2,0],[1,2,0]]
T3L = [[1,1,1],[2,2,2],[0,0,0]]

def parse_expr(s):
    s = s.strip()
    while s[0] == '(' and _m(s,0) == len(s)-1: s = s[1:-1].strip()
    d = 0
    for i,c in enumerate(s):
        if c == '(': d+=1
        elif c == ')': d-=1
        elif c == '*' and d==0:
            return ('*', parse_expr(s[:i]), parse_expr(s[i+1:]))
    return s.strip()

def _m(s,p):
    d=1
    for i in range(p+1,len(s)):
        if s[i]=='(': d+=1
        elif s[i]==')':
            d-=1
            if d==0: return i
    return -1

def get_vars(e1,e2):
    seen=[]
    for c in e1+' '+e2:
        if c.isalpha() and c not in seen: seen.append(c)
    return seen

def assign(vo): return {v:i%3 for i,v in enumerate(vo)}

def ev(t,a,tb):
    if isinstance(t,str): return a[t]
    return tb[ev(t[1],a,tb)][ev(t[2],a,tb)]

def check(e1,e2,table):
    e1l,e1r=e1.split('=',1); e2l,e2r=e2.split('=',1)
    vo=get_vars(e1,e2); a=assign(vo); nv=len(vo)
    if ev(parse_expr(e1l),a,table)!=ev(parse_expr(e1r),a,table): return 'E1F',nv
    if ev(parse_expr(e2l),a,table)!=ev(parse_expr(e2r),a,table): return 'SEP',nv
    return 'HOLD',nv

bms = [
    ('hard3', 'data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl'),
    ('normal', 'data/benchmark/normal_balanced60_true30_false30_rotation0020_20260417_002534.jsonl'),
]

for bname,bpath in bms:
    print(f"\n{'='*60}\n  {bname}\n{'='*60}")
    
    # Check each magma independently
    for mname, table in [('T3R',T3R),('T3L',T3L),('T4A',T4A),('T5B',T5B)]:
        true_fn=[]  # TRUE falsely separated
        false_ok=[]  # FALSE correctly separated
        
        with open(bpath) as f:
            for line in f:
                p=json.loads(line)
                r,nv=check(p['equation1'],p['equation2'],table)
                if p['answer']:
                    if r=='SEP': true_fn.append((p['id'],nv))
                else:
                    if r=='SEP': false_ok.append((p['id'],nv))
        
        fn3=[x for x in true_fn if x[1]<=3]
        ok3=[x for x in false_ok if x[1]<=3]
        print(f"\n  {mname}: {len(false_ok)} FALSE caught, {len(true_fn)} TRUE FN")
        print(f"    ≤3-var: {len(ok3)} FALSE caught, {len(fn3)} TRUE FN")
        if fn3:
            print(f"    FN (≤3v): {fn3}")
    
    # Combined: T3R+T3L+T5B with ≤3-var gate for T5B
    print(f"\n  Combined T3R+T3L+T5B(≤3v):")
    total_true_fn=0; total_false_ok=0; total_true=0; total_false=0
    with open(bpath) as f:
        for line in f:
            p=json.loads(line)
            e1,e2=p['equation1'],p['equation2']
            gt=p['answer']
            vo=get_vars(e1,e2); nv=len(vo)
            
            if gt: total_true+=1
            else: total_false+=1
            
            sep=False
            for mname,table in [('T3R',T3R),('T3L',T3L)]:
                r,_=check(e1,e2,table)
                if r=='SEP': sep=True; break
            
            if not sep and nv<=3:
                r,_=check(e1,e2,T5B)
                if r=='SEP': sep=True
            
            if gt and sep: total_true_fn+=1
            if not gt and sep: total_false_ok+=1
    
    print(f"    TRUE: {total_true-total_true_fn}/{total_true} safe, {total_true_fn} FN")
    print(f"    FALSE caught: {total_false_ok}/{total_false}")
    
    # Also check T3R+T3L+T5B(≤3v)+T4A(≤2v) or T3R+T3L+T5B(all)
    for label, max_t5b, max_t4a in [
        ("T3R+T3L+T5B(all)", 99, -1),
        ("T3R+T3L+T4A(≤3v)+T5B(≤3v)", 3, 3),
    ]:
        total_true_fn=0; total_false_ok=0
        with open(bpath) as f:
            for line in f:
                p=json.loads(line)
                e1,e2=p['equation1'],p['equation2']
                gt=p['answer']
                vo=get_vars(e1,e2); nv=len(vo)
                
                sep=False
                for mname,table in [('T3R',T3R),('T3L',T3L)]:
                    r,_=check(e1,e2,table)
                    if r=='SEP': sep=True; break
                
                if not sep and nv<=max_t4a:
                    r,_=check(e1,e2,T4A)
                    if r=='SEP': sep=True
                
                if not sep and nv<=max_t5b:
                    r,_=check(e1,e2,T5B)
                    if r=='SEP': sep=True
                
                if gt and sep: total_true_fn+=1
                if not gt and sep: total_false_ok+=1
        
        print(f"\n  {label}:")
        print(f"    TRUE FN: {total_true_fn}, FALSE caught: {total_false_ok}")
