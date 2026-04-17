"""Quick safety check: NL1 and NL2 on rotation0021 TRUE problems."""
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

magmas = {
    'NL1': [[0,0,0],[1,1,0],[1,2,2]],
    'NL2': [[0,1,1],[0,1,2],[1,1,2]],
}

# Check on rotation0021
with open('data/benchmark/hard3_balanced20_true10_false10_rotation0021_20260417_041003.jsonl') as f:
    rows = [json.loads(l) for l in f if l.strip()]

true_rows = [r for r in rows if r['answer'] == True]
false_rows = [r for r in rows if r['answer'] == False]
print(f"Benchmark: {len(true_rows)} TRUE, {len(false_rows)} FALSE")

for mname, table in magmas.items():
    print(f"\n=== {mname} ===")
    fn_count = 0
    catch_count = 0
    for r in rows:
        all_v = get_vars(r['equation1'] + ' ' + r['equation2'])
        nv = len(all_v)
        if nv > 3:
            continue  # gated at ≤3 vars
        e1p = r['equation1'].split('=',1)
        e2p = r['equation2'].split('=',1)
        e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
        e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
        
        default = list(range(nv))
        e1_ok = e1_fn(table, default)
        e2_ok = e2_fn(table, default)
        
        if r['answer'] == True:
            if e1_ok and not e2_ok:
                fn_count += 1
                print(f"  FN! {r['id']} ({nv}v): E1={e1_ok} E2={e2_ok}")
        else:
            if e1_ok and not e2_ok:
                catch_count += 1
                print(f"  CATCH {r['id']} ({nv}v)")
    
    print(f"  FN: {fn_count}, Catches: {catch_count}")

# Also check on a bigger TRUE set for safety
import glob
normal_files = glob.glob('data/benchmark/normal_*.jsonl')
if normal_files:
    normal_file = sorted(normal_files)[-1]
    print(f"\n=== Safety check on {normal_file} ===")
    with open(normal_file) as f:
        nrows = [json.loads(l) for l in f if l.strip()]
    
    true_normal = [r for r in nrows if r['answer'] == True]
    print(f"TRUE problems: {len(true_normal)}")
    
    for mname, table in magmas.items():
        fn = 0
        for r in true_normal:
            all_v = get_vars(r['equation1'] + ' ' + r['equation2'])
            nv = len(all_v)
            if nv > 3: continue
            e1p = r['equation1'].split('=',1)
            e2p = r['equation2'].split('=',1)
            e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
            e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
            default = list(range(nv))
            if e1_fn(table, default) and not e2_fn(table, default):
                fn += 1
                print(f"  {mname} FN: {r['id']} ({nv}v)")
        print(f"  {mname}: {fn} FN on normal TRUE set")
