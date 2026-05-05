"""Analyze the persistent coverage-gap FP pairs on normal."""
import json

pairs = [json.loads(l) for l in open('data/benchmark/normal_balanced60_true30_false30_rotation0002_20260403_185904.jsonl')]
false_p = [p for p in pairs if not p.get('answer')]

gaps = ['normal_0884', 'normal_0335', 'normal_0618', 'normal_0301']

def parse_eq(eq):
    parts = eq.split('=', 1)
    return parts[0].strip(), parts[1].strip()

def first_letter(e):
    for c in e:
        if c.isalpha(): return c

def last_letter(e):
    for c in reversed(e):
        if c.isalpha(): return c

def left_depth(e):
    if '*' not in e: return 0
    for i, c in enumerate(e):
        if c.isalpha(): return e[:i].count('(') + 1
    return 0

def right_depth(e):
    if '*' not in e: return 0
    for i in range(len(e)-1, -1, -1):
        if e[i].isalpha(): return e[i+1:].count(')') + 1
    return 0

import re
def var_set(e):
    return set(re.findall(r'[a-z]', e))

def star_count(e):
    return e.count('*')

for pid in gaps:
    p = [x for x in false_p if x['id'] == pid]
    if not p:
        print(f"{pid}: NOT FOUND in benchmark")
        continue
    p = p[0]
    e1, e2 = p['equation1'], p['equation2']
    print(f"=== {pid} ===")
    print(f"  E1: {e1}")
    print(f"  E2: {e2}")
    
    l1, r1 = parse_eq(e1)
    l2, r2 = parse_eq(e2)
    
    print(f"  E1 L: fl={first_letter(l1)} ll={last_letter(l1)} ld={left_depth(l1)} rd={right_depth(l1)} vars={var_set(l1)} stars={star_count(l1)}")
    print(f"  E1 R: fl={first_letter(r1)} ll={last_letter(r1)} ld={left_depth(r1)} rd={right_depth(r1)} vars={var_set(r1)} stars={star_count(r1)}")
    print(f"  E2 L: fl={first_letter(l2)} ll={last_letter(l2)} ld={left_depth(l2)} rd={right_depth(l2)} vars={var_set(l2)} stars={star_count(l2)}")
    print(f"  E2 R: fl={first_letter(r2)} ll={last_letter(r2)} ld={left_depth(r2)} rd={right_depth(r2)} vars={var_set(r2)} stars={star_count(r2)}")
    
    # Check what test COULD separate
    tests = {}
    tests['LP'] = (first_letter(l1)==first_letter(r1), first_letter(l2)==first_letter(r2))
    tests['RP'] = (last_letter(l1)==last_letter(r1), last_letter(l2)==last_letter(r2))
    tests['C0'] = ('*' in l1) == ('*' in r1) if '*' in l1 or '*' in r1 else l1.strip()==r1.strip(), \
                  ('*' in l2) == ('*' in r2) if '*' in l2 or '*' in r2 else l2.strip()==r2.strip()
    
    l3_e1 = first_letter(l1)==first_letter(r1) and left_depth(l1)%3==left_depth(r1)%3
    l3_e2 = first_letter(l2)==first_letter(r2) and left_depth(l2)%3==left_depth(r2)%3
    d3_e1 = last_letter(l1)==last_letter(r1) and right_depth(l1)%3==right_depth(r1)%3
    d3_e2 = last_letter(l2)==last_letter(r2) and right_depth(l2)%3==right_depth(r2)%3
    
    stars_e1 = star_count(l1) == star_count(r1)
    stars_e2 = star_count(l2) == star_count(r2)
    
    varcount_e1 = len(var_set(l1)) == len(var_set(r1))
    varcount_e2 = len(var_set(l2)) == len(var_set(r2))
    
    print(f"  L3: E1={'H' if l3_e1 else 'F'} E2={'H' if l3_e2 else 'F'} sep={'Y' if l3_e1 and not l3_e2 else 'N'}")
    print(f"  D3: E1={'H' if d3_e1 else 'F'} E2={'H' if d3_e2 else 'F'} sep={'Y' if d3_e1 and not d3_e2 else 'N'}")
    print(f"  Stars: E1={'H' if stars_e1 else 'F'} E2={'H' if stars_e2 else 'F'} sep={'Y' if stars_e1 and not stars_e2 else 'N'}")
    print(f"  VarCount: E1={'H' if varcount_e1 else 'F'} E2={'H' if varcount_e2 else 'F'} sep={'Y' if varcount_e1 and not varcount_e2 else 'N'}")
    print()
