"""Check which magmas catch uncaught FALSE problems on DEFAULT assignment specifically."""
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

# The 5 uncaught FALSE problems
problems = [
    ('hard3_0175', 'x = (y * z) * (x * (z * x))', 'x * y = ((x * x) * y) * y'),
    ('hard3_0191', 'x = (y * x) * ((x * z) * x)', 'x * y = x * (x * (z * y))'),
    ('hard3_0189', 'x = (y * x) * ((x * x) * x)', 'x = ((y * z) * z) * (z * x)'),
    ('hard3_0322', 'x = ((y * (z * y)) * z) * x', 'x * x = (x * (y * y)) * x'),
    ('hard3_0253', 'x = (x * (y * (y * z))) * y', 'x * (x * y) = x * (z * z)'),
]

for pid, e1, e2 in problems:
    all_v = get_vars(e1 + ' ' + e2)
    nv = len(all_v)
    e1p = e1.split('=',1); e2p = e2.split('=',1)
    e1_fn = eval(f'lambda t,v: ({parse_to_code(e1p[0],all_v)}) == ({parse_to_code(e1p[1],all_v)})')
    e2_fn = eval(f'lambda t,v: ({parse_to_code(e2p[0],all_v)}) == ({parse_to_code(e2p[1],all_v)})')
    
    default = list(range(nv)) + [0]*(3-nv)  # pad if < 3 vars
    default = default[:nv]
    
    print(f"\n=== {pid} ({nv}v) default={default} ===")
    print(f"  E1: {e1}")
    print(f"  E2: {e2}")
    
    # Search for magma where E1 holds on default AND E2 fails on default
    found = 0
    best = None
    for tbl_flat in itertools.product(range(3), repeat=9):
        t = [list(tbl_flat[j*3:(j+1)*3]) for j in range(3)]
        if e1_fn(t, default) and not e2_fn(t, default):
            if found == 0:
                best = [row[:] for row in t]
                print(f"  DEFAULT-CATCH magma: {t}")
                # Also check: is this magma safe? (no FN on TRUE problems)
                # Skip full safety for now, just show first hit
            found += 1
    
    if found == 0:
        print(f"  NO magma catches on default assignment!")
        print(f"  (Must use non-default assignment or this problem is uncatchable with single-assignment)")
    else:
        print(f"  Total default-catching magmas: {found}")
        
        # For the first one found, verify E1 fails universally? No - check what happens
        # Also check if any KNOWN magma catches on default
        known = {
            'T3R': [[1,2,0],[1,2,0],[1,2,0]],
            'T3L': [[1,1,1],[2,2,2],[0,0,0]],
            'T5B': [[0,2,1],[1,0,2],[2,1,0]],
            'M1':  [[0,0,0],[1,1,0],[1,2,2]],
            'NEW': [[0,1,1],[0,1,2],[1,1,2]],
        }
        for name, t in known.items():
            e1_default = e1_fn(t, default)
            e2_default = e2_fn(t, default)
            marker = "CATCH!" if (e1_default and not e2_default) else ""
            print(f"  {name}: E1={e1_default} E2={e2_default} {marker}")
