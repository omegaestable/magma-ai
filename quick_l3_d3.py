"""Quick focused L3 vs D3 comparison on key benchmarks."""
import json

def parse_equation(eq_str):
    parts = eq_str.split('=', 1)
    return parts[0].strip(), parts[1].strip()

def first_letter(expr):
    for ch in expr:
        if ch.isalpha(): return ch
    return None

def last_letter(expr):
    for ch in reversed(expr):
        if ch.isalpha(): return ch
    return None

def left_depth(expr):
    if '*' not in expr: return 0
    for i, ch in enumerate(expr):
        if ch.isalpha(): return expr[:i].count('(') + 1
    return 0

def right_depth(expr):
    if '*' not in expr: return 0
    for i in range(len(expr)-1, -1, -1):
        if expr[i].isalpha(): return expr[i+1:].count(')') + 1
    return 0

def l3_holds(eq_str):
    lhs, rhs = parse_equation(eq_str)
    return first_letter(lhs) == first_letter(rhs) and left_depth(lhs) % 3 == left_depth(rhs) % 3

def d3_holds(eq_str):
    lhs, rhs = parse_equation(eq_str)
    return last_letter(lhs) == last_letter(rhs) and right_depth(lhs) % 3 == right_depth(rhs) % 3

def lp_holds(eq_str):
    lhs, rhs = parse_equation(eq_str)
    return first_letter(lhs) == first_letter(rhs)

def rp_holds(eq_str):
    lhs, rhs = parse_equation(eq_str)
    return last_letter(lhs) == last_letter(rhs)

def c0_holds(eq_str):
    lhs, rhs = parse_equation(eq_str)
    l_has, r_has = '*' in lhs, '*' in rhs
    if l_has and r_has: return True
    if not l_has and not r_has: return lhs.strip() == rhs.strip()
    return False

benchmarks = [
    ('NORMAL-60', 'data/benchmark/normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl'),
    ('HARD3-40', 'data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl'),
    ('HARD2-40', 'data/benchmark/hard_balanced40_true20_false20_rotation0001_20260403_163406.jsonl'),
]

for label, path in benchmarks:
    pairs = [json.loads(l) for l in open(path)]
    false_p = [p for p in pairs if not p.get('label', p.get('answer'))]
    true_p = [p for p in pairs if p.get('label', p.get('answer'))]
    
    print(f"=== {label} ({len(false_p)}F/{len(true_p)}T) ===")
    
    catches = {'LP':[], 'RP':[], 'C0':[], 'L3':[], 'D3':[]}
    for p in false_p:
        e1, e2 = p['equation1'], p['equation2']
        for name, fn in [('LP', lp_holds), ('RP', rp_holds), ('C0', c0_holds), ('L3', l3_holds), ('D3', d3_holds)]:
            if fn(e1) and not fn(e2):
                catches[name].append(p['id'])
    
    base = set(catches['LP']) | set(catches['RP']) | set(catches['C0'])
    l3_new = [x for x in catches['L3'] if x not in base]
    d3_new = [x for x in catches['D3'] if x not in base]
    
    print(f"  LP={len(catches['LP'])} RP={len(catches['RP'])} C0={len(catches['C0'])} | base={len(base)}/{len(false_p)}")
    print(f"  L3={len(catches['L3'])} (new={len(l3_new)}) D3={len(catches['D3'])} (new={len(d3_new)})")
    combined = base | set(catches['L3']) | set(catches['D3'])
    print(f"  LP+RP+C0+L3+D3 = {len(combined)}/{len(false_p)}")
    
    if l3_new:
        print(f"  L3 novel catches: {l3_new}")
        for pid in l3_new:
            p = [x for x in false_p if x['id'] == pid][0]
            e1, e2 = p['equation1'], p['equation2']
            lhs1, rhs1 = parse_equation(e1)
            lhs2, rhs2 = parse_equation(e2)
            print(f"    {pid}: E1: {e1}")
            print(f"           E2: {e2}")
            print(f"    E1 L: first={first_letter(lhs1)} ld={left_depth(lhs1)} | R: first={first_letter(rhs1)} ld={left_depth(rhs1)}")
            print(f"    E2 L: first={first_letter(lhs2)} ld={left_depth(lhs2)} | R: first={first_letter(rhs2)} ld={left_depth(rhs2)}")
    
    if d3_new:
        print(f"  D3 novel catches: {d3_new}")
        for pid in d3_new:
            p = [x for x in false_p if x['id'] == pid][0]
            e1, e2 = p['equation1'], p['equation2']
            lhs1, rhs1 = parse_equation(e1)
            lhs2, rhs2 = parse_equation(e2)
            print(f"    {pid}: E1: {e1}")
            print(f"           E2: {e2}")
            print(f"    E1 L: last={last_letter(lhs1)} rd={right_depth(lhs1)} | R: last={last_letter(rhs1)} rd={right_depth(rhs1)}")
            print(f"    E2 L: last={last_letter(lhs2)} rd={right_depth(lhs2)} | R: last={last_letter(rhs2)} rd={right_depth(rhs2)}")
    
    l3ff = sum(1 for p in true_p if l3_holds(p['equation1']) and not l3_holds(p['equation2']))
    d3ff = sum(1 for p in true_p if d3_holds(p['equation1']) and not d3_holds(p['equation2']))
    print(f"  False flags: L3={l3ff}/{len(true_p)} D3={d3ff}/{len(true_p)}")
    print()
