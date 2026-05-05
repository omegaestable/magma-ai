"""Safety check M1 magma on benchmarks."""
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

M1 = [[0,0,0],[1,1,0],[1,2,2]]

def check_magma(rows, magma, label):
    fn_count = 0
    catch_count = 0
    for row in rows:
        pid = row.get('id') or row.get('problem_id')
        gt = row.get('answer') if 'answer' in row else row.get('ground_truth')
        e1 = row['equation1']; e2 = row['equation2']
        all_v = get_vars(e1 + ' ' + e2)
        e1p = e1.split('=',1); e2p = e2.split('=',1)
        e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
        e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
        asgns = list(itertools.product(range(3), repeat=len(all_v)))
        e1_ok = all(e1_fn(magma, v) for v in asgns)
        e2_ok = all(e2_fn(magma, v) for v in asgns)
        sep = e1_ok and not e2_ok
        if gt == True and sep:
            print(f"  FN DANGER: {pid} vars={len(all_v)} E1:{e1[:60]} E2:{e2[:60]}")
            fn_count += 1
        elif gt == False and sep:
            catch_count += 1
    print(f"  {label}: {catch_count} FALSE catches, {fn_count} TRUE FN")
    return fn_count

# New benchmark
with open('data/benchmark/hard3_balanced20_true10_false10_rotation0021_20260417_041003.jsonl', encoding='utf-8') as f:
    new_rows = [json.loads(line) for line in f if line.strip()]

print("=== M1 on NEW hard3 (universal check) ===")
check_magma(new_rows, M1, "New benchmark")

# Old hard3
with open('results/v26h_hard3_50.json', encoding='utf-8') as f:
    old_data = json.load(f)

print("\n=== M1 on OLD hard3 TRUE (universal check) ===")
old_true = [r for r in old_data['results'] if r['ground_truth'] == True]
fn_old = 0
for r in old_true:
    e1 = r['equation1']; e2 = r['equation2']
    all_v = get_vars(e1 + ' ' + e2)
    e1p = e1.split('=',1); e2p = e2.split('=',1)
    e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
    e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
    asgns = list(itertools.product(range(3), repeat=len(all_v)))
    e1_ok = all(e1_fn(M1, v) for v in asgns)
    e2_ok = all(e2_fn(M1, v) for v in asgns)
    if e1_ok and not e2_ok:
        print(f"  FN DANGER: {r['id']} E1:{e1[:60]} E2:{e2[:60]}")
        fn_old += 1
print(f"  Old TRUE: {fn_old} FN")

# Default assignment check on new benchmark
print("\n=== M1 DEFAULT ASSIGNMENT ONLY (new benchmark) ===")
fn_def = 0; catch_def = 0
for row in new_rows:
    pid = row['id']; gt = row['answer']; e1 = row['equation1']; e2 = row['equation2']
    all_v = get_vars(e1 + ' ' + e2)
    e1p = e1.split('=',1); e2p = e2.split('=',1)
    e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
    e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
    default_v = tuple(i % 3 for i in range(len(all_v)))
    e1_def = e1_fn(M1, default_v)
    e2_def = e2_fn(M1, default_v)
    if e1_def and not e2_def:
        if gt == True:
            print(f"  FN (default): {pid} vars={len(all_v)}")
            fn_def += 1
        elif gt == False:
            catch_def += 1
print(f"  Default only: {catch_def} catches, {fn_def} FN")
