"""Compute coverage matrix and greedy set cover for FP errors."""
import json, re, itertools

with open('results/v26h_hard3_50.json', encoding='utf-8') as f:
    data = json.load(f)

fps = [r for r in data['results'] if r['ground_truth'] == False and r['predicted'] == True]

def get_vars(eq):
    return sorted(set(re.findall(r'[a-z]', eq)))

def parse_to_code(expr_str, var_list):
    s = expr_str.strip()
    def parse(s):
        s = s.strip()
        depth = 0; main_op = -1
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            elif c == '*' and depth == 0: main_op = i; break
        if main_op == -1:
            if s.startswith('(') and s.endswith(')'): return parse(s[1:-1])
            return f'v[{var_list.index(s.strip())}]'
        return f't[{parse(s[:main_op].strip())}][{parse(s[main_op+1:].strip())}]'
    return parse(s)

fp_data = []
for r in fps:
    pid = r['id']; e1 = r['equation1']; e2 = r['equation2']
    all_v = get_vars(e1 + ' ' + e2)
    e1p = e1.split('=',1); e2p = e2.split('=',1)
    e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
    e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
    fp_data.append({'id':pid, 'nv':len(all_v), 'e1_fn':e1_fn, 'e2_fn':e2_fn})

all_asgn = {nv: list(itertools.product(range(3), repeat=nv)) for nv in range(1,6)}

# Compute coverage
print('Computing coverage matrix for ALL 19683 size-3 magmas...')
coverage = {}
for i, tbl_flat in enumerate(itertools.product(range(3), repeat=9)):
    t = [list(tbl_flat[j*3:(j+1)*3]) for j in range(3)]
    hits = set()
    for fp in fp_data:
        asgns = all_asgn[fp['nv']]
        e1_ok = all(fp['e1_fn'](t, v) for v in asgns)
        if e1_ok:
            e2_ok = all(fp['e2_fn'](t, v) for v in asgns)
            if not e2_ok:
                hits.add(fp['id'])
    if hits:
        coverage[i] = (tbl_flat, hits)

print(f'Found {len(coverage)} magmas with coverage > 0')

# Per-problem coverage count
covered_by = {}
for _, (_, hits) in coverage.items():
    for pid in hits:
        covered_by[pid] = covered_by.get(pid, 0) + 1

print('\nPer-problem coverage:')
for fp in fp_data:
    c = covered_by.get(fp['id'], 0)
    label = "EXECUTION ERROR (T3R should catch)" if fp['id'] == 'hard3_0013' else ""
    print(f"  {fp['id']} ({fp['nv']}v): {c} magmas {label}")

# Greedy set cover
uncovered = set(fp['id'] for fp in fp_data if fp['id'] in covered_by)
print(f'\nTotal coverable FPs: {len(uncovered)}/15')

selected = []
while uncovered:
    best_idx = None
    best_gain = 0
    for idx, (tbl_flat, hits) in coverage.items():
        gain = len(hits & uncovered)
        if gain > best_gain:
            best_gain = gain
            best_idx = idx
    if best_gain == 0:
        break
    tbl_flat, hits = coverage[best_idx]
    covered = hits & uncovered
    t = [list(tbl_flat[j*3:(j+1)*3]) for j in range(3)]
    selected.append((t, sorted(covered)))
    uncovered -= covered
    print(f'  Selected: {t} covers {sorted(covered)} (+{best_gain})')

all_covered = set()
for _, c in selected:
    all_covered.update(c)
all_fp_ids = set(fp['id'] for fp in fp_data)
print(f'\nGreedy covering: {len(selected)} magmas cover {len(all_covered)} FPs')
print(f'Uncoverable (need size 4+): {sorted(all_fp_ids - all_covered)}')

# Describe selected magmas
print('\n=== SELECTED MAGMA DESCRIPTIONS ===')
for t, covered in selected:
    print(f'\nMagma {t}:')
    for a in range(3):
        print(f'  {a}*0={t[a][0]}  {a}*1={t[a][1]}  {a}*2={t[a][2]}')
    # Check if it's a linear magma
    for ca in range(3):
        for cb in range(3):
            for cc in range(3):
                ok = True
                for a in range(3):
                    for b in range(3):
                        if (ca*a + cb*b + cc) % 3 != t[a][b]:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    print(f'  → Linear: a*b = ({ca}a + {cb}b + {cc}) mod 3')
    print(f'  Covers: {covered}')
