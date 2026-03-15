import csv, re
from collections import Counter, defaultdict

rows = []
with open('data/exports/export_explorer_14_3_2026.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

eq_key = list(rows[0].keys())[0]

def parse_eq(eq_str):
    m = re.match(r'Equation(\d+)\[(.+)\]', eq_str)
    if not m: return None, None
    return int(m.group(1)), m.group(2)

OP = '\u25c7'  # ◇

def count_ops(s): return s.count(OP)
def term_depth(s):
    depth = maxd = 0
    for c in s:
        if c == '(': depth += 1; maxd = max(maxd, depth)
        elif c == ')': depth -= 1
    return maxd
def get_vars(s): return set(re.findall(r'[a-z]', s))
def var_mults(s): return Counter(re.findall(r'[a-z]', s))
def is_singleton(lhs, rhs):
    lv = get_vars(lhs); rv = get_vars(rhs)
    if lv.isdisjoint(rv) and (OP in lhs or OP in rhs): return True
    if len(lv)==1 and not (lv & rv): return True
    if len(rv)==1 and not (lv & rv): return True
    return False

eq_data = {}
for r in rows:
    num, formula = parse_eq(r[eq_key])
    if num is None: continue
    try:
        lhs, rhs = formula.split('=', 1)
        lhs = lhs.strip(); rhs = rhs.strip()
    except:
        continue
    lm = var_mults(lhs); rm = var_mults(rhs)
    all_vars = set(list(lm.keys())+list(rm.keys()))
    balanced = all(lm.get(v,0)==rm.get(v,0) for v in all_vars)
    distinct = len(get_vars(formula))
    total_ops = count_ops(lhs) + count_ops(rhs)
    max_depth = max(term_depth(lhs), term_depth(rhs))
    lhs_ops = count_ops(lhs); rhs_ops = count_ops(rhs)
    repeated = any(lm.get(v,0)>1 or rm.get(v,0)>1 for v in all_vars)
    lhs_is_var = bool(re.fullmatch(r'[a-z]', lhs))
    rhs_is_var = bool(re.fullmatch(r'[a-z]', rhs))
    singleton = is_singleton(lhs, rhs)
    vars_shared = len(get_vars(lhs) & get_vars(rhs))
    eq_data[num] = {
        'formula': formula, 'lhs': lhs, 'rhs': rhs,
        'implies': int(r['Implies']),
        'implied_by': int(r['Implied by']),
        'total_ops': total_ops,
        'lhs_ops': lhs_ops, 'rhs_ops': rhs_ops,
        'max_depth': max_depth,
        'distinct_vars': distinct,
        'balanced': balanced,
        'repeated': repeated,
        'singleton': singleton,
        'lhs_is_var': lhs_is_var,
        'rhs_is_var': rhs_is_var,
        'vars_shared': vars_shared,
    }

all_imp = [d['implies'] for d in eq_data.values()]
all_impby = [d['implied_by'] for d in eq_data.values()]
print(f'Loaded {len(eq_data)} equations')
print(f'Out-degree: min={min(all_imp)} max={max(all_imp)} mean={sum(all_imp)/len(all_imp):.1f}')
print(f'In-degree:  min={min(all_impby)} max={max(all_impby)} mean={sum(all_impby)/len(all_impby):.1f}')

print('\n=== Total ops (order) vs implies ===')  
for ops in range(0, 9):
    sub = [d for d in eq_data.values() if d['total_ops']==ops]
    if sub:
        ai = sum(d['implies'] for d in sub)/len(sub)
        ab = sum(d['implied_by'] for d in sub)/len(sub)
        print(f'  ops={ops}: n={len(sub):4d}  avg_implies={ai:7.1f}  avg_implied_by={ab:7.1f}')

print('\n=== Max depth vs implies ===')  
for d in range(0, 6):
    sub = [x for x in eq_data.values() if x['max_depth']==d]
    if sub:
        ai = sum(x['implies'] for x in sub)/len(sub)
        ab = sum(x['implied_by'] for x in sub)/len(sub)
        print(f'  depth={d}: n={len(sub):4d}  avg_implies={ai:7.1f}  avg_implied_by={ab:7.1f}')

print('\n=== Distinct vars vs implies ===')  
for nv in range(1, 6):
    sub = [d for d in eq_data.values() if d['distinct_vars']==nv]
    if sub:
        ai = sum(x['implies'] for x in sub)/len(sub)
        ab = sum(x['implied_by'] for x in sub)/len(sub)
        print(f'  vars={nv}: n={len(sub):4d}  avg_implies={ai:7.1f}  avg_implied_by={ab:7.1f}')

print('\n=== Key binary features ===')
for feat, label in [('singleton','singleton'), ('balanced','balanced_vars'), ('repeated','repeated_vars'), ('lhs_is_var','lhs_is_var')]:
    yes = [d for d in eq_data.values() if d[feat]]
    no = [d for d in eq_data.values() if not d[feat]]
    ai_yes = sum(d['implies'] for d in yes)/len(yes) if yes else 0
    ab_yes = sum(d['implied_by'] for d in yes)/len(yes) if yes else 0
    ai_no = sum(d['implies'] for d in no)/len(no) if no else 0
    ab_no = sum(d['implied_by'] for d in no)/len(no) if no else 0
    print(f'  {label}=T: n={len(yes):4d}  avg_imp={ai_yes:7.1f}  avg_impby={ab_yes:7.1f}')
    print(f'  {label}=F: n={len(no):4d}  avg_imp={ai_no:7.1f}  avg_impby={ab_no:7.1f}')

print('\n=== Top 20 hubs ===')
top = sorted(eq_data.items(), key=lambda x: -x[1]['implies'])[:20]
for num, d in top:
    s = int(d['singleton']); b = int(d['balanced']); r = int(d['repeated'])
    print(f'  Eq{num:5d}: {d["formula"]:<50s}  imp={d["implies"]:5d}  ops={d["total_ops"]}  vars={d["distinct_vars"]}  depth={d["max_depth"]}  s={s}  b={b}  r={r}')

print('\n=== Top 20 sinks (high in-degree) ===')
top_s = sorted(eq_data.items(), key=lambda x: -x[1]['implied_by'])[:20]
for num, d in top_s:
    b = int(d['balanced']); r = int(d['repeated'])
    print(f'  Eq{num:5d}: {d["formula"]:<50s}  impby={d["implied_by"]:5d}  ops={d["total_ops"]}  vars={d["distinct_vars"]}  b={b}  r={r}')

print('\n=== Out-degree histogram ===')
for lo, hi in [(0,1),(1,5),(5,20),(20,50),(50,100),(100,300),(300,700),(700,2000),(2000,5000)]:
    c = sum(1 for d in eq_data.values() if lo<=d['implies']<hi)
    print(f'  [{lo:5d},{hi:5d}): {c:5d} equations')

print('\n=== ops x implies bucket ===')
for ops in range(0, 9):
    sub = [d for d in eq_data.values() if d['total_ops']==ops]
    if not sub: continue
    b0=b1=b10=b50=b100=b500=0
    for d in sub:
        v = d['implies']
        if v>=500: b500+=1
        elif v>=100: b100+=1
        elif v>=50: b50+=1
        elif v>=10: b10+=1
        elif v>=1: b1+=1
        else: b0+=1
    print(f'  ops={ops} (n={len(sub):4d}): 0={b0:3d} 1-9={b1:3d} 10-49={b10:3d} 50-99={b50:3d} 100-499={b100:3d} 500+={b500:3d}')

print('\n=== Complex but weak (ops>=4, implies<10) ===')
cww = [(num,d) for num,d in eq_data.items() if d['total_ops']>=4 and d['implies']<10]
cww.sort(key=lambda x: x[1]['total_ops'], reverse=True)
for num,d in cww[:15]:
    print(f'  Eq{num}: {d["formula"]}   ops={d["total_ops"]}  implies={d["implies"]}  vars={d["distinct_vars"]}  balanced={d["balanced"]}')

print('\n=== Simple but powerful (ops<=2, implies>=100) ===')
sbp = [(num,d) for num,d in eq_data.items() if d['total_ops']<=2 and d['implies']>=100]
sbp.sort(key=lambda x: -x[1]['implies'])
for num,d in sbp[:20]:
    print(f'  Eq{num}: {d["formula"]}   ops={d["total_ops"]}  implies={d["implies"]}  vars={d["distinct_vars"]}  singleton={d["singleton"]}')

print('\n=== Asymmetry (LHS ops != RHS ops breakdown) ===')
for ops_asym in range(0, 6):
    sub = [d for d in eq_data.values() if abs(d['lhs_ops']-d['rhs_ops'])==ops_asym]
    if sub:
        ai = sum(d['implies'] for d in sub)/len(sub)
        ab = sum(d['implied_by'] for d in sub)/len(sub)
        print(f'  asym={ops_asym}: n={len(sub):4d}  avg_implies={ai:7.1f}  avg_implied_by={ab:7.1f}')

print('\n=== vars_shared ===')
for vs in range(0, 5):
    sub = [d for d in eq_data.values() if d['vars_shared']==vs]
    if sub:
        ai = sum(d['implies'] for d in sub)/len(sub)
        ab = sum(d['implied_by'] for d in sub)/len(sub)
        print(f'  vars_shared={vs}: n={len(sub):4d}  avg_implies={ai:7.1f}  avg_implied_by={ab:7.1f}')

print('\n=== One-var laws (idempotent-type) ===')
ov = [(num,d) for num,d in eq_data.items() if d['distinct_vars']==1]
ov.sort(key=lambda x: -x[1]['implied_by'])
for num,d in ov[:15]:
    print(f'  Eq{num}: {d["formula"]}   ops={d["total_ops"]}  implies={d["implies"]}  impby={d["implied_by"]}')

print('\n=== LHS=x laws with 3+ ops on RHS ===')
lxr = [(num,d) for num,d in eq_data.items() if d['lhs_is_var'] and d['rhs_ops']>=3]
lxr.sort(key=lambda x: -x[1]['implies'])
for num,d in lxr[:15]:
    print(f'  Eq{num}: {d["formula"]}   rhs_ops={d["rhs_ops"]}  implies={d["implies"]}  vars={d["distinct_vars"]}')

print('\n=== Equations where singleton detection triggers ===')
sf = [(num,d) for num,d in eq_data.items() if d['singleton']]
sf.sort(key=lambda x: -x[1]['implies'])
for num,d in sf[:20]:
    print(f'  Eq{num}: {d["formula"]}   ops={d["total_ops"]}  implies={d["implies"]}  depth={d["max_depth"]}  vars={d["distinct_vars"]}')
