"""Check if v26h normal FP misses are catchable by ungated T3R/T3L."""
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

# Load normal benchmark
with open('data/benchmark/normal_balanced60_true30_false30_rotation0020_20260417_002534.jsonl', encoding='utf-8') as f:
    rows = [json.loads(l) for l in f if l.strip()]

# Missed FALSE problems (FP)
fp_ids = ['normal_0971','normal_0837','normal_0446','normal_0356','normal_0340','normal_0276']

magmas = {
    'T3R': [[1,2,0],[1,2,0],[1,2,0]],
    'T3L': [[1,1,1],[2,2,2],[0,0,0]],
    'T5B': [[0,2,1],[1,0,2],[2,1,0]],
    'NL1': [[0,0,0],[1,1,0],[1,2,2]],
}

for row in rows:
    if row['id'] not in fp_ids:
        continue
    e1, e2 = row['equation1'], row['equation2']
    all_v = get_vars(e1 + ' ' + e2)
    nv = len(all_v)
    e1p = e1.split('=',1); e2p = e2.split('=',1)
    e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
    e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
    
    # LP/RP
    def first_letter(s):
        for c in s:
            if c.isalpha(): return c
        return None
    def last_letter(s):
        for c in reversed(s):
            if c.isalpha(): return c
        return None
    
    e1_lp = first_letter(e1p[0]) == first_letter(e1p[1])
    e2_lp = first_letter(e2p[0]) == first_letter(e2p[1])
    e1_rp = last_letter(e1p[0]) == last_letter(e1p[1])
    e2_rp = last_letter(e2p[0]) == last_letter(e2p[1])
    
    default = list(range(nv))
    print(f"\n{row['id']} ({nv}v) LP:E1={'H' if e1_lp else 'F'} E2={'H' if e2_lp else 'F'} RP:E1={'H' if e1_rp else 'F'} E2={'H' if e2_rp else 'F'}")
    print(f"  E1: {e1}")
    print(f"  E2: {e2}")
    
    for mname, t in magmas.items():
        if mname in ('T5B','NL1') and nv > 3:
            continue
        e1_ok = e1_fn(t, default)
        e2_ok = e2_fn(t, default)
        gated_out = False
        if mname == 'T3R' and not e1_rp:
            gated_out = True
        if mname == 'T3L' and not e1_lp:
            gated_out = True
        marker = " CATCH!" if (e1_ok and not e2_ok) else ""
        gate_marker = " (GATED OUT)" if gated_out else ""
        print(f"  {mname}: E1={e1_ok} E2={e2_ok}{marker}{gate_marker}")
