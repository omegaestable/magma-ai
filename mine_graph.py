import csv, re, math
from collections import defaultdict, Counter

# Load equations from explorer CSV
rows = []
with open('data/exports/export_explorer_14_3_2026.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

eq_key = list(rows[0].keys())[0]  # handle BOM

# Parse equation numbers and formulas
eq_data = {}
for r in rows:
    eq_str = r[eq_key]  # e.g. 'Equation1[x = x]'
    m = re.match(r'Equation(\d+)\[(.+)\]', eq_str)
    if m:
        num = int(m.group(1))
        formula = m.group(2)
        eq_data[num] = {
            'formula': formula,
            'implies': int(r['Implies']),
            'implied_by': int(r['Implied by']),
            'not_implies': int(r['Does not imply']),
            'not_implied_by': int(r['Not implied by']),
        }

print(f'Loaded {len(eq_data)} equations')

def parse_formula(f):
    lhs, rhs = f.split('=', 1)
    return lhs.strip(), rhs.strip()

def term_depth(s):
    depth = 0; max_d = 0
    for c in s:
        if c == '(': depth += 1; max_d = max(max_d, depth)
        elif c == ')': depth -= 1
    return max_d

def count_ops(s):
    return s.count('*')

def count_vars_distinct(s):
    return len(set(re.findall(r'[a-z]', s)))

def count_var_occurrences(s):
    return len(re.findall(r'[a-z]', s))

def var_multiplicities(s):
    return Counter(re.findall(r'[a-z]', s))

def is_singleton_forcing(lhs, rhs):
    lv = set(re.findall(r'[a-z]', lhs))
    rv = set(re.findall(r'[a-z]', rhs))
    if lv.isdisjoint(rv) and ('*' in lhs or '*' in rhs):
        return True
    if len(lv)==1 and not (lv & rv):
        return True
    if len(rv)==1 and not (lv & rv):
        return True
    return False

# Compute features
for num, d in eq_data.items():
    f = d['formula']
    try:
        lhs, rhs = parse_formula(f)
        d['lhs'] = lhs; d['rhs'] = rhs
        d['lhs_ops'] = count_ops(lhs)
        d['rhs_ops'] = count_ops(rhs)
        d['total_ops'] = d['lhs_ops'] + d['rhs_ops']
        d['lhs_depth'] = term_depth(lhs)
        d['rhs_depth'] = term_depth(rhs)
        d['max_depth'] = max(d['lhs_depth'], d['rhs_depth'])
        d['total_distinct_vars'] = len(set(re.findall(r'[a-z]', f)))
        d['total_var_occurrences'] = count_var_occurrences(lhs) + count_var_occurrences(rhs)
        d['singleton_forcing'] = is_singleton_forcing(lhs, rhs)
        lm = var_multiplicities(lhs); rm = var_multiplicities(rhs)
        all_vars = set(list(lm.keys()) + list(rm.keys()))
        d['balanced_vars'] = all(lm.get(v,0)==rm.get(v,0) for v in all_vars)
        d['repeated_vars'] = any(lm.get(v,0)>1 or rm.get(v,0)>1 for v in all_vars)
        # lhs is single variable?
        d['lhs_is_var'] = bool(re.fullmatch(r'[a-z]', lhs))
        d['rhs_is_var'] = bool(re.fullmatch(r'[a-z]', rhs))
        # Asymmetry: one side has strictly more ops
        d['ops_asymmetry'] = abs(d['lhs_ops'] - d['rhs_ops'])
        # Variable reuse: same var on both sides at all?
        d['vars_shared'] = len(set(re.findall(r'[a-z]', lhs)) & set(re.findall(r'[a-z]', rhs)))
    except:
        d['lhs'] = d['rhs'] = ''; d['total_ops'] = 0; d['max_depth'] = 0
        d['total_distinct_vars'] = 0; d['singleton_forcing'] = False
        d['balanced_vars'] = False; d['repeated_vars'] = False
        d['lhs_is_var'] = False; d['rhs_is_var'] = False; d['ops_asymmetry'] = 0; d['vars_shared'] = 0

all_implies = [d['implies'] for d in eq_data.values()]
all_implied = [d['implied_by'] for d in eq_data.values()]
print(f'Out-degree: min={min(all_implies)}, max={max(all_implies)}, mean={sum(all_implies)/len(all_implies):.1f}')
print(f'In-degree: min={min(all_implied)}, max={max(all_implied)}, mean={sum(all_implied)/len(all_implied):.1f}')

# Top hubs
top_hubs = sorted(eq_data.items(), key=lambda x: x[1]['implies'], reverse=True)[:20]
print('\nTop 20 hubs (highest out-degree):')
for num, d in top_hubs:
    print(f"  Eq{num}: [{d['formula']}]  implies={d['implies']}  ops={d.get('total_ops')}  vars={d.get('total_distinct_vars')}  depth={d.get('max_depth')}  singleton={d.get('singleton_forcing')}  balanced={d.get('balanced_vars')}")

# Top sinks
print('\nTop 15 sinks (highest in-degree):')
top_sinks = sorted(eq_data.items(), key=lambda x: x[1]['implied_by'], reverse=True)[:15]
for num, d in top_sinks:
    print(f"  Eq{num}: [{d['formula']}]  implied_by={d['implied_by']}  ops={d.get('total_ops')}  vars={d.get('total_distinct_vars')}  lhs_is_var={d.get('lhs_is_var')}  rhs_is_var={d.get('rhs_is_var')}")

# Correlation: ops vs implies
print('\n--- Correlation: total_ops vs implies ---')
for ops in range(0, 9):
    subset = [d for d in eq_data.values() if d.get('total_ops')==ops]
    if subset:
        avg_imp = sum(d['implies'] for d in subset)/len(subset)
        avg_impby = sum(d['implied_by'] for d in subset)/len(subset)
        print(f"  ops={ops}: n={len(subset)}  avg_implies={avg_imp:.1f}  avg_implied_by={avg_impby:.1f}")

print('\n--- Correlation: max_depth vs implies ---')
for depth in range(0, 5):
    subset = [d for d in eq_data.values() if d.get('max_depth')==depth]
    if subset:
        avg_imp = sum(d['implies'] for d in subset)/len(subset)
        avg_impby = sum(d['implied_by'] for d in subset)/len(subset)
        print(f"  depth={depth}: n={len(subset)}  avg_implies={avg_imp:.1f}  avg_implied_by={avg_impby:.1f}")

print('\n--- Singleton forcing ---')
sf_yes = [d for d in eq_data.values() if d.get('singleton_forcing')]
sf_no = [d for d in eq_data.values() if not d.get('singleton_forcing')]
if sf_yes:
    print(f"  Singleton-forcing: n={len(sf_yes)}  avg_implies={sum(d['implies'] for d in sf_yes)/len(sf_yes):.1f}  avg_implied_by={sum(d['implied_by'] for d in sf_yes)/len(sf_yes):.1f}")
if sf_no:
    print(f"  Non-singleton: n={len(sf_no)}  avg_implies={sum(d['implies'] for d in sf_no)/len(sf_no):.1f}  avg_implied_by={sum(d['implied_by'] for d in sf_no)/len(sf_no):.1f}")

print('\n--- Balanced vars ---')
bv_yes = [d for d in eq_data.values() if d.get('balanced_vars')]
bv_no = [d for d in eq_data.values() if not d.get('balanced_vars')]
if bv_yes:
    print(f"  Balanced: n={len(bv_yes)}  avg_implies={sum(d['implies'] for d in bv_yes)/len(bv_yes):.1f}  avg_implied_by={sum(d['implied_by'] for d in bv_yes)/len(bv_yes):.1f}")
if bv_no:
    print(f"  Unbalanced: n={len(bv_no)}  avg_implies={sum(d['implies'] for d in bv_no)/len(bv_no):.1f}  avg_implied_by={sum(d['implied_by'] for d in bv_no)/len(bv_no):.1f}")

print('\n--- Repeated vars ---')
rv_yes = [d for d in eq_data.values() if d.get('repeated_vars')]
rv_no = [d for d in eq_data.values() if not d.get('repeated_vars')]
if rv_yes:
    print(f"  Repeated: n={len(rv_yes)}  avg_implies={sum(d['implies'] for d in rv_yes)/len(rv_yes):.1f}  avg_implied_by={sum(d['implied_by'] for d in rv_yes)/len(rv_yes):.1f}")
if rv_no:
    print(f"  No repeat: n={len(rv_no)}  avg_implies={sum(d['implies'] for d in rv_no)/len(rv_no):.1f}  avg_implied_by={sum(d['implied_by'] for d in rv_no)/len(rv_no):.1f}")

print('\n--- LHS is single var ---')
lv_yes = [d for d in eq_data.values() if d.get('lhs_is_var')]
lv_no = [d for d in eq_data.values() if not d.get('lhs_is_var')]
if lv_yes:
    print(f"  LHS is var: n={len(lv_yes)}  avg_implies={sum(d['implies'] for d in lv_yes)/len(lv_yes):.1f}  avg_implied_by={sum(d['implied_by'] for d in lv_yes)/len(lv_yes):.1f}")
if lv_no:
    print(f"  LHS not var: n={len(lv_no)}  avg_implies={sum(d['implies'] for d in lv_no)/len(lv_no):.1f}  avg_implied_by={sum(d['implied_by'] for d in lv_no)/len(lv_no):.1f}")

print('\n--- Distinct vars ---')
for nv in range(1, 6):
    subset = [d for d in eq_data.values() if d.get('total_distinct_vars')==nv]
    if subset:
        avg_imp = sum(d['implies'] for d in subset)/len(subset)
        avg_impby = sum(d['implied_by'] for d in subset)/len(subset)
        print(f"  distinct_vars={nv}: n={len(subset)}  avg_implies={avg_imp:.1f}  avg_implied_by={avg_impby:.1f}")

# Implication bucketing
print('\n--- Out-degree distribution ---')
buckets = [0, 1, 10, 50, 100, 500, 1000, 2000, 4694]
for i in range(len(buckets)-1):
    count = sum(1 for d in eq_data.values() if buckets[i] <= d['implies'] < buckets[i+1])
    print(f"  implies in [{buckets[i]},{buckets[i+1]}): {count}")

# Extreme low-implication non-trivial equations
print('\n--- Low implies (0-5, non-trivial formulas) ---')
low_imp = [(num, d) for num, d in eq_data.items() if d['implies'] <= 5 and d.get('total_ops',0) >= 2]
low_imp.sort(key=lambda x: x[1]['implies'])
for num, d in low_imp[:20]:
    print(f"  Eq{num}: [{d['formula']}]  implies={d['implies']}  ops={d.get('total_ops')}  vars={d.get('total_distinct_vars')}  balanced={d.get('balanced_vars')}")

# Order-1 laws (1 op total)
print('\n--- All order-1 laws ---')
o1 = [(num, d) for num, d in eq_data.items() if d.get('total_ops',0)==1]
o1.sort(key=lambda x: -x[1]['implies'])
for num, d in o1:
    print(f"  Eq{num}: [{d['formula']}]  implies={d['implies']}  implied_by={d['implied_by']}")

# Formula pattern detection: LHS=x patterns
print('\n--- LHS=x (projection/collapse laws) ---')
lhs_x = [(num, d) for num, d in eq_data.items() if d.get('lhs_is_var') and d.get('rhs_ops',0)>=2]
lhs_x.sort(key=lambda x: -x[1]['implies'])
for num, d in lhs_x[:15]:
    print(f"  Eq{num}: [{d['formula']}]  implies={d['implies']}  ops={d.get('total_ops')}  vars={d.get('total_distinct_vars')}")
