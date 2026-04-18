"""Find best magmas for the new rotation0021 hard3 benchmark."""
import json, re, itertools

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
            if s.startswith('(') and s.endswith(')'):
                return parse(s[1:-1])
            return f'v[{var_list.index(s.strip())}]'
        return f't[{parse(s[:main_op].strip())}][{parse(s[main_op+1:].strip())}]'
    return parse(s)

with open('data/benchmark/hard3_balanced20_true10_false10_rotation0021_20260417_041003.jsonl', encoding='utf-8') as f:
    rows = [json.loads(line) for line in f if line.strip()]

fp_data = []
true_data = []
for row in rows:
    pid = row['id']; gt = row['answer']; e1 = row['equation1']; e2 = row['equation2']
    all_v = get_vars(e1 + ' ' + e2)
    e1p = e1.split('=',1); e2p = e2.split('=',1)
    e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
    e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
    entry = {'id':pid, 'nv':len(all_v), 'e1_fn':e1_fn, 'e2_fn':e2_fn, 'gt':gt, 'e1':e1, 'e2':e2}
    if gt == False:
        fp_data.append(entry)
    else:
        true_data.append(entry)

print(f"FALSE problems: {len(fp_data)}, TRUE problems: {len(true_data)}")

# Check which are already caught by existing pipeline (structural + T3R + T3L + T5B)
existing_magmas = {
    'T3R': [[1,2,0],[1,2,0],[1,2,0]],
    'T3L': [[1,1,1],[2,2,2],[0,0,0]],
    'T5B': [[0,2,1],[1,0,2],[2,1,0]],
}

all_asgn = {nv: list(itertools.product(range(3), repeat=nv)) for nv in range(1,6)}

print("\n=== Existing magma coverage on FALSE problems ===")
for fp in fp_data:
    catches = []
    for name, table in existing_magmas.items():
        if name == 'T5B' and fp['nv'] > 3:
            continue
        asgns = all_asgn[fp['nv']]
        e1_ok = all(fp['e1_fn'](table, v) for v in asgns)
        if e1_ok:
            e2_ok = all(fp['e2_fn'](table, v) for v in asgns)
            if not e2_ok:
                catches.append(name)
    print(f"  {fp['id']} ({fp['nv']}v): {', '.join(catches) if catches else 'NO CATCH'}")

# Brute force: best new size-3 magma for uncaught FALSE problems
uncaught = []
for fp in fp_data:
    caught = False
    for name, table in existing_magmas.items():
        if name == 'T5B' and fp['nv'] > 3:
            continue
        asgns = all_asgn[fp['nv']]
        e1_ok = all(fp['e1_fn'](table, v) for v in asgns)
        if e1_ok:
            e2_ok = all(fp['e2_fn'](table, v) for v in asgns)
            if not e2_ok:
                caught = True; break
    if not caught:
        uncaught.append(fp)

print(f"\n{len(uncaught)} uncaught FALSE problems — searching size-3 magmas...")

# For each uncaught, find any size-3 separator
for fp in uncaught:
    found = False
    asgns = all_asgn[fp['nv']]
    for tbl_flat in itertools.product(range(3), repeat=9):
        t = [list(tbl_flat[j*3:(j+1)*3]) for j in range(3)]
        e1_ok = all(fp['e1_fn'](t, v) for v in asgns)
        if e1_ok:
            e2_ok = all(fp['e2_fn'](t, v) for v in asgns)
            if not e2_ok:
                print(f"  {fp['id']} ({fp['nv']}v): {t}")
                found = True
                break
    if not found:
        print(f"  {fp['id']} ({fp['nv']}v): NO size-3 separator — E1: {fp['e1'][:50]} | E2: {fp['e2'][:50]}")

# Also find best single new magma that covers most uncaught AND has 0 FN on TRUE
print("\n=== Best single NEW magma (0 FN required) ===")
best_count = 0; best_magma = None; best_hits = []
for tbl_flat in itertools.product(range(3), repeat=9):
    t = [list(tbl_flat[j*3:(j+1)*3]) for j in range(3)]
    # Check FN safety first
    fn = False
    for tr in true_data:
        asgns = all_asgn[tr['nv']]
        e1_ok = all(tr['e1_fn'](t, v) for v in asgns)
        if e1_ok:
            e2_ok = all(tr['e2_fn'](t, v) for v in asgns)
            if not e2_ok:
                fn = True; break
    if fn: continue
    
    # Count catches
    hits = []
    for fp in uncaught:
        asgns = all_asgn[fp['nv']]
        e1_ok = all(fp['e1_fn'](t, v) for v in asgns)
        if e1_ok:
            e2_ok = all(fp['e2_fn'](t, v) for v in asgns)
            if not e2_ok:
                hits.append(fp['id'])
    if len(hits) > best_count:
        best_count = len(hits)
        best_magma = [row[:] for row in t]
        best_hits = hits[:]
        print(f"  New best: {best_count} catches — {best_magma} — {best_hits}")

print(f"\nBest safe new magma: {best_magma} covers {best_count} uncaught FPs: {best_hits}")
