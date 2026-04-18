"""Brute-force search for size-2 and size-3 magma separators for v26h FP errors."""
import json, re, itertools, time

with open('results/v26h_hard3_50.json', encoding='utf-8') as f:
    data = json.load(f)

fps = [r for r in data['results'] if r['ground_truth'] == False and r['predicted'] == True]
fns = [r for r in data['results'] if r['ground_truth'] == True and r['predicted'] == False]

def get_vars(eq):
    return sorted(set(re.findall(r'[a-z]', eq)))

def parse_to_code(expr_str, var_list):
    s = expr_str.strip()
    def parse(s):
        s = s.strip()
        depth = 0
        main_op = -1
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            elif c == '*' and depth == 0:
                main_op = i
                break
        if main_op == -1:
            if s.startswith('(') and s.endswith(')'):
                return parse(s[1:-1])
            v = s.strip()
            idx = var_list.index(v)
            return f'v[{idx}]'
        left = s[:main_op].strip()
        right = s[main_op+1:].strip()
        return f't[{parse(left)}][{parse(right)}]'
    return parse(s)

fp_data = []
for r in fps + fns:
    pid = r['id']
    gt = r['ground_truth']
    e1 = r['equation1']
    e2 = r['equation2']
    all_v = get_vars(e1 + ' ' + e2)
    e1_parts = e1.split('=', 1)
    e2_parts = e2.split('=', 1)
    
    e1l_code = parse_to_code(e1_parts[0], all_v)
    e1r_code = parse_to_code(e1_parts[1], all_v)
    e2l_code = parse_to_code(e2_parts[0], all_v)
    e2r_code = parse_to_code(e2_parts[1], all_v)
    
    e1_fn = eval(f'lambda t, v: ({e1l_code}) == ({e1r_code})')
    e2_fn = eval(f'lambda t, v: ({e2l_code}) == ({e2r_code})')
    
    fp_data.append({
        'id': pid,
        'nv': len(all_v),
        'gt': gt,
        'e1_fn': e1_fn,
        'e2_fn': e2_fn,
        'e1': e1,
        'e2': e2,
    })

# --- Size-2 ---
print('=== SIZE 2 (16 magmas) ===')
all_asgn_2 = {nv: list(itertools.product(range(2), repeat=nv)) for nv in range(1,6)}

for fp in fp_data:
    nv = fp['nv']
    asgns = all_asgn_2.get(nv, list(itertools.product(range(2), repeat=nv)))
    found = False
    for tbl_flat in itertools.product(range(2), repeat=4):
        t = [[tbl_flat[0], tbl_flat[1]], [tbl_flat[2], tbl_flat[3]]]
        e1_ok = all(fp['e1_fn'](t, v) for v in asgns)
        if e1_ok:
            e2_ok = all(fp['e2_fn'](t, v) for v in asgns)
            if not e2_ok:
                print(f"  {fp['id']}: SEPARATED by {t}")
                found = True
                break
    if not found:
        print(f"  {fp['id']}: no size-2")

# --- Size-3 ---
print()
print('=== SIZE 3 (19683 magmas) ===')
all_asgn_3 = {nv: list(itertools.product(range(3), repeat=nv)) for nv in range(1,6)}

t0 = time.time()
for idx, fp in enumerate(fp_data):
    nv = fp['nv']
    asgns = all_asgn_3.get(nv, list(itertools.product(range(3), repeat=nv)))
    found = False
    for tbl_flat in itertools.product(range(3), repeat=9):
        t = [list(tbl_flat[i*3:(i+1)*3]) for i in range(3)]
        e1_ok = all(fp['e1_fn'](t, v) for v in asgns)
        if e1_ok:
            e2_ok = all(fp['e2_fn'](t, v) for v in asgns)
            if not e2_ok:
                print(f"  {fp['id']} ({nv}v): {t}")
                found = True
                break
    if not found:
        print(f"  {fp['id']} ({nv}v): no size-3")
    if (idx + 1) % 4 == 0:
        elapsed = time.time() - t0
        print(f"  ... {idx+1}/{len(fp_data)} done in {elapsed:.1f}s")

print(f"\nTotal time: {time.time()-t0:.1f}s")
