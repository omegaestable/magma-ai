"""
Verify L3 test (LSUCC3 universal check via text inspection).

LSUCC3 magma: x◇y = NEXT(x) where NEXT cycles 0→1→2→0.
Table: [[1,1,1],[2,2,2],[0,0,0]]  (row i, all columns = (i+1)%3)

For LSUCC3: eval(term, assignment) = (assignment[first_var] + left_depth) mod 3
where left_depth = number of * operations on the leftmost evaluation path.

Text inspection equivalent:
  left_depth(bare variable) = 0
  left_depth(has *) = (count of opening parens at start before first letter) + 1

LSUCC3 universally satisfies "A = B" iff:
  first_letter(A) == first_letter(B) AND left_depth(A) ≡ left_depth(B) mod 3

This script verifies this equivalence on all benchmark pairs and checks for false flags.
"""

import json, re, itertools

def parse_equation(eq_str):
    """Split 'LHS = RHS' into (lhs, rhs)."""
    parts = eq_str.split('=', 1)
    return parts[0].strip(), parts[1].strip()

def first_letter(expr):
    """First a-z letter in expression (scan past opening parens)."""
    for ch in expr:
        if ch.isalpha():
            return ch
    return None

def last_letter(expr):
    """Last a-z letter in expression (scan past closing parens)."""
    for ch in reversed(expr):
        if ch.isalpha():
            return ch
    return None

def left_depth(expr):
    """Left-depth: bare variable → 0. Has * → (opening parens before first letter) + 1."""
    if '*' not in expr:
        return 0
    for i, ch in enumerate(expr):
        if ch.isalpha():
            return expr[:i].count('(') + 1
    return 0

def right_depth(expr):
    """Right-depth (D3): bare variable → 0. Has * → (closing parens after last letter) + 1."""
    if '*' not in expr:
        return 0
    for i in range(len(expr) - 1, -1, -1):
        if expr[i].isalpha():
            return expr[i+1:].count(')') + 1
    return 0

def l3_check(expr):
    """L3 test for one side: returns (first_letter, left_depth mod 3)."""
    return (first_letter(expr), left_depth(expr) % 3)

def l3_holds(eq_str):
    """L3 HOLD for an equation: same first letter AND same left_depth mod 3 on both sides."""
    lhs, rhs = parse_equation(eq_str)
    fl_l, ld_l = l3_check(lhs)
    fl_r, ld_r = l3_check(rhs)
    return fl_l == fl_r and ld_l == ld_r

def d3_check(expr):
    """D3 test for one side: returns (last_letter, right_depth mod 3)."""
    return (last_letter(expr), right_depth(expr) % 3)

def d3_holds(eq_str):
    """D3 HOLD for an equation."""
    lhs, rhs = parse_equation(eq_str)
    ll_l, rd_l = d3_check(lhs)
    ll_r, rd_r = d3_check(rhs)
    return ll_l == ll_r and rd_l == rd_r

def lp_holds(eq_str):
    """LP test: same first letter on both sides."""
    lhs, rhs = parse_equation(eq_str)
    return first_letter(lhs) == first_letter(rhs)

def rp_holds(eq_str):
    """RP test: same last letter on both sides."""
    lhs, rhs = parse_equation(eq_str)
    return last_letter(lhs) == last_letter(rhs)

def c0_holds(eq_str):
    """C0 test: both sides have * or neither has * (with same variable)."""
    lhs, rhs = parse_equation(eq_str)
    l_has = '*' in lhs
    r_has = '*' in rhs
    if l_has and r_has:
        return True
    if not l_has and not r_has:
        return lhs.strip() == rhs.strip()
    return False

# --- Brute-force LSUCC3 universal check ---
LSUCC3 = [[1,1,1],[2,2,2],[0,0,0]]

def get_variables(expr):
    return sorted(set(re.findall(r'[a-z]', expr)))

def eval_magma(expr, assignment, table):
    """Evaluate expression on a magma given variable assignment."""
    expr = expr.replace(' ', '')
    pos = [0]
    
    def parse_expr():
        result = parse_atom()
        while pos[0] < len(expr) and expr[pos[0]] == '*':
            pos[0] += 1  # skip *
            right = parse_atom()
            result = table[result][right]
        return result
    
    def parse_atom():
        if expr[pos[0]] == '(':
            pos[0] += 1  # skip (
            result = parse_expr()
            pos[0] += 1  # skip )
            return result
        else:
            var = expr[pos[0]]
            pos[0] += 1
            return assignment[var]
    
    return parse_expr()

def check_equation_universal(eq_str, table):
    """Check if equation holds on magma for ALL assignments."""
    lhs, rhs = parse_equation(eq_str)
    variables = sorted(set(get_variables(lhs) + get_variables(rhs)))
    n = len(table)
    
    for values in itertools.product(range(n), repeat=len(variables)):
        assignment = dict(zip(variables, values))
        l_val = eval_magma(lhs, assignment, table)
        r_val = eval_magma(rhs, assignment, table)
        if l_val != r_val:
            return False
    return True

# --- Load benchmark data ---
import glob

benchmarks = {}
for path in sorted(glob.glob('data/benchmark/*.jsonl')):
    name = path.split('\\')[-1].split('/')[-1]
    pairs = []
    with open(path) as f:
        for line in f:
            pairs.append(json.loads(line))
    benchmarks[name] = pairs

# --- Process all pairs ---
print("=" * 80)
print("L3 (LSUCC3) vs D3 (RSUCC3) COMPARISON ON ALL BENCHMARK PAIRS")
print("=" * 80)

for bname, pairs in sorted(benchmarks.items()):
    if 'normal' not in bname and 'hard' not in bname:
        continue
    
    print(f"\n{'='*60}")
    print(f"Benchmark: {bname} ({len(pairs)} pairs)")
    print(f"{'='*60}")
    
    true_pairs = [p for p in pairs if p.get('label', p.get('answer'))]
    false_pairs = [p for p in pairs if not p.get('label', p.get('answer'))]
    
    # Check what each test catches on FALSE pairs (separation = E1 holds, E2 fails)
    lp_catches = []
    rp_catches = []
    c0_catches = []
    l3_catches = []
    d3_catches = []
    
    for p in false_pairs:
        e1, e2 = p['equation1'], p['equation2']
        
        lp_e1, lp_e2 = lp_holds(e1), lp_holds(e2)
        rp_e1, rp_e2 = rp_holds(e1), rp_holds(e2)
        c0_e1, c0_e2 = c0_holds(e1), c0_holds(e2)
        l3_e1, l3_e2 = l3_holds(e1), l3_holds(e2)
        d3_e1, d3_e2 = d3_holds(e1), d3_holds(e2)
        
        if lp_e1 and not lp_e2: lp_catches.append(p['id'])
        if rp_e1 and not rp_e2: rp_catches.append(p['id'])
        if c0_e1 and not c0_e2: c0_catches.append(p['id'])
        if l3_e1 and not l3_e2: l3_catches.append(p['id'])
        if d3_e1 and not d3_e2: d3_catches.append(p['id'])
    
    print(f"\nFALSE pairs separation (E1=HOLD, E2=FAIL):")
    print(f"  LP catches: {len(lp_catches)}/{len(false_pairs)}")
    print(f"  RP catches: {len(rp_catches)}/{len(false_pairs)}")
    print(f"  C0 catches: {len(c0_catches)}/{len(false_pairs)}")
    print(f"  L3 catches: {len(l3_catches)}/{len(false_pairs)}")
    print(f"  D3 catches: {len(d3_catches)}/{len(false_pairs)}")
    
    # L3-only catches (not caught by LP/RP/C0)
    lp_rp_c0 = set(lp_catches) | set(rp_catches) | set(c0_catches)
    l3_only = [x for x in l3_catches if x not in lp_rp_c0]
    d3_only = [x for x in d3_catches if x not in lp_rp_c0]
    l3_new = [x for x in l3_catches if x not in lp_rp_c0 and x not in d3_catches]
    
    print(f"\n  L3 NEW catches (not in LP/RP/C0): {len(l3_only)} {l3_only}")
    print(f"  D3 NEW catches (not in LP/RP/C0): {len(d3_only)} {d3_only}")
    print(f"  L3 catches NOT in D3: {len(l3_new)} {l3_new}")
    
    # Combined coverage
    all_four = set(lp_catches) | set(rp_catches) | set(c0_catches) | set(l3_catches)
    all_with_d3 = lp_rp_c0 | set(d3_catches)
    all_five = all_four | set(d3_catches)
    
    print(f"\n  LP+RP+C0 coverage: {len(lp_rp_c0)}/{len(false_pairs)}")
    print(f"  LP+RP+C0+L3 coverage: {len(all_four)}/{len(false_pairs)}")
    print(f"  LP+RP+C0+D3 coverage: {len(all_with_d3)}/{len(false_pairs)}")
    print(f"  LP+RP+C0+L3+D3 coverage: {len(all_five)}/{len(false_pairs)}")
    
    # False flags on TRUE pairs
    l3_false_flags = 0
    d3_false_flags = 0
    for p in true_pairs:
        e1, e2 = p['equation1'], p['equation2']
        l3_e1, l3_e2 = l3_holds(e1), l3_holds(e2)
        d3_e1, d3_e2 = d3_holds(e1), d3_holds(e2)
        if l3_e1 and not l3_e2:
            l3_false_flags += 1
        if d3_e1 and not d3_e2:
            d3_false_flags += 1
    
    print(f"\n  L3 false flags on TRUE: {l3_false_flags}/{len(true_pairs)}")
    print(f"  D3 false flags on TRUE: {d3_false_flags}/{len(true_pairs)}")
    
    # Verify L3 text test matches LSUCC3 brute-force (on a subset)
    if 'hard3' in bname:
        print(f"\n  --- LSUCC3 brute-force verification ---")
        mismatches = 0
        for p in false_pairs:
            e1, e2 = p['equation1'], p['equation2']
            bf_e1 = check_equation_universal(e1, LSUCC3)
            bf_e2 = check_equation_universal(e2, LSUCC3)
            bf_sep = bf_e1 and not bf_e2
            
            l3_e1_h, l3_e2_h = l3_holds(e1), l3_holds(e2)
            l3_sep = l3_e1_h and not l3_e2_h
            
            if bf_sep != l3_sep:
                mismatches += 1
                print(f"    MISMATCH {p['id']}: brute={bf_sep} l3={l3_sep}")
                print(f"      E1: {e1}")
                print(f"      E2: {e2}")
                lhs1, rhs1 = parse_equation(e1)
                lhs2, rhs2 = parse_equation(e2)
                print(f"      E1 L: first={first_letter(lhs1)} ldepth={left_depth(lhs1)} | R: first={first_letter(rhs1)} ldepth={left_depth(rhs1)}")
                print(f"      E2 L: first={first_letter(lhs2)} ldepth={left_depth(lhs2)} | R: first={first_letter(rhs2)} ldepth={left_depth(rhs2)}")
                print(f"      BF: e1={bf_e1} e2={bf_e2}")
        
        if mismatches == 0:
            print(f"    ✓ Zero mismatches — L3 text test is exactly LSUCC3 universal check")
        
        # Also verify on TRUE pairs
        for p in true_pairs:
            e1, e2 = p['equation1'], p['equation2']
            bf_e1 = check_equation_universal(e1, LSUCC3)
            bf_e2 = check_equation_universal(e2, LSUCC3)
            bf_sep = bf_e1 and not bf_e2
            
            l3_e1_h, l3_e2_h = l3_holds(e1), l3_holds(e2)
            l3_sep = l3_e1_h and not l3_e2_h
            
            if bf_sep != l3_sep:
                mismatches += 1
                print(f"    TRUE MISMATCH {p['id']}: brute={bf_sep} l3={l3_sep}")
        
        if mismatches == 0:
            print(f"    ✓ Confirmed on both TRUE and FALSE — L3 ≡ LSUCC3 universal")

    # Show details of L3 catches on hard3
    if 'hard3' in bname and l3_catches:
        print(f"\n  --- L3 separation details ---")
        for pid in l3_catches:
            p = [x for x in false_pairs if x['id'] == pid][0]
            e1, e2 = p['equation1'], p['equation2']
            lhs1, rhs1 = parse_equation(e1)
            lhs2, rhs2 = parse_equation(e2)
            print(f"  {pid}:")
            print(f"    E1: {e1}")
            print(f"    E2: {e2}")
            print(f"    E1 L: first={first_letter(lhs1)} ldepth={left_depth(lhs1)} | R: first={first_letter(rhs1)} ldepth={left_depth(rhs1)}")
            print(f"    E2 L: first={first_letter(lhs2)} ldepth={left_depth(lhs2)} | R: first={first_letter(rhs2)} ldepth={left_depth(rhs2)}")
            in_other = "also LP/RP/C0" if pid in lp_rp_c0 else "L3-ONLY (NEW!)"
            print(f"    Coverage: {in_other}")
