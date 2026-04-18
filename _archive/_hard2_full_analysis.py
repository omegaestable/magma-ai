"""Full analysis: structural tests + magma tests on hard2 FALSE problems."""
import json, re

data = [json.loads(l) for l in open('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl')]
false_probs = [d for d in data if not d['answer']]

def assign_vars(e1, e2):
    full = e1 + ' ' + e2
    seen = []
    for c in full:
        if c.isalpha() and c not in seen:
            seen.append(c)
    mapping = {}
    for i, v in enumerate(seen):
        mapping[v] = i % 3
    return mapping

def eval_magma(expr, table_fn):
    s = expr.replace(' ', '')
    while '*' in s:
        m = re.search(r'\((\d)\*(\d)\)', s)
        if not m:
            m = re.search(r'(\d)\*(\d)', s)
        if not m:
            break
        a, b = int(m.group(1)), int(m.group(2))
        s = s[:m.start()] + str(table_fn(a, b)) + s[m.end():]
    s = s.replace('(', '').replace(')', '')
    return int(s) if s.isdigit() else -1

t3r = lambda a, b: (b + 1) % 3
t3l = lambda a, b: (a + 1) % 3
t5b = lambda a, b: (a + 2*b) % 3
nl1_tbl = {(0,0):0,(0,1):0,(0,2):0,(1,0):1,(1,1):1,(1,2):0,(2,0):1,(2,1):2,(2,2):2}
nl1 = lambda a, b: nl1_tbl[(a, b)]

def rewrite(expr, mapping):
    return ''.join(str(mapping[c]) if c.isalpha() else c for c in expr)

def first_letter(s):
    for c in s:
        if c.isalpha():
            return c
    return None

def last_letter(s):
    for c in reversed(s):
        if c.isalpha():
            return c
    return None

def has_star(s):
    return '*' in s

def var_set(s):
    return set(c for c in s if c.isalpha())

def var_counts(s):
    counts = {}
    for c in s:
        if c.isalpha():
            counts[c] = counts.get(c, 0) + 1
    return counts

def ldepth(s):
    """Count * nodes from root to leftmost letter, always going left."""
    s = s.strip()
    depth = 0
    i = 0
    while i < len(s):
        if s[i] == '(':
            depth += 0  # just skip opening parens
            i += 1
        elif s[i].isalpha():
            return depth
        elif s[i] == '*':
            return depth  # shouldn't get here in well-formed
        elif s[i] == ')' or s[i] == ' ':
            i += 1
        else:
            i += 1
    return depth

def ldepth_proper(s):
    """Count * operations on the left spine path."""
    s = s.strip()
    # Parse and count depth of * operations going left
    depth = 0
    i = 0
    while i < len(s):
        if s[i] == '(':
            i += 1
            continue
        elif s[i].isalpha():
            return depth
        elif s[i] == ' ':
            i += 1
            continue
        elif s[i] == '*':
            depth += 1
            # now we need to skip the right subtree
            # actually this is tricky, let me use a different approach
            return depth
        else:
            i += 1
    return depth

def count_star_depth_left(expr):
    """Count * nodes from root going always-left to reach leftmost letter."""
    expr = expr.strip()
    pos = 0  
    depth = 0
    while pos < len(expr):
        c = expr[pos]
        if c == '(':
            pos += 1
        elif c.isalpha():
            return depth
        elif c == ' ':
            pos += 1
        elif c == '*':
            # We hit a *, but if we're nested we may reach this
            # Actually in the tree, * appears after the left subtree
            # Let me just count opening parens before first letter
            break
        else:
            pos += 1
    
    # Alternative: count the depth by counting how many * are on left spine
    # For "x*y" → 1, "(x*y)*z" → 2, "((x*y)*z)*w" → 3, "x*(y*z)" → 1
    # This equals: number of opening ( before first letter, if those ( lead to left children
    # Actually simplest: parse the tree
    
    # Simple recursive descent
    def parse(s, pos):
        # Skip whitespace
        while pos < len(s) and s[pos] == ' ':
            pos += 1
        if pos >= len(s):
            return (0, pos)
        
        if s[pos] == '(':
            # Grouped expression
            pos += 1  # skip (
            left_depth, pos = parse(s, pos)
            # skip whitespace
            while pos < len(s) and s[pos] == ' ':
                pos += 1
            # expect *
            if pos < len(s) and s[pos] == '*':
                pos += 1
                # skip right subtree
                paren_depth = 0
                while pos < len(s):
                    if s[pos] == '(':
                        paren_depth += 1
                    elif s[pos] == ')':
                        if paren_depth == 0:
                            break
                        paren_depth -= 1
                    pos += 1
                pos += 1  # skip closing )
                return (left_depth + 1, pos)
            else:
                # skip to closing )
                paren_depth = 0
                while pos < len(s):
                    if s[pos] == ')':
                        if paren_depth == 0:
                            pos += 1
                            break
                        paren_depth -= 1
                    elif s[pos] == '(':
                        paren_depth += 1
                    pos += 1
                return (left_depth, pos)
        elif s[pos].isalpha():
            pos += 1
            # Check if followed by * (infix without parens: "x * y")
            save = pos
            while pos < len(s) and s[pos] == ' ':
                pos += 1
            if pos < len(s) and s[pos] == '*':
                pos += 1
                # skip right subtree
                while pos < len(s) and s[pos] == ' ':
                    pos += 1
                paren_depth = 0
                while pos < len(s):
                    if s[pos] == '(':
                        paren_depth += 1
                    elif s[pos] == ')':
                        if paren_depth == 0:
                            break
                        paren_depth -= 1
                    elif s[pos].isalpha() and paren_depth == 0:
                        pos += 1
                        break
                    pos += 1
                return (1, pos)
            else:
                return (0, save)
        return (0, pos)
    
    d, _ = parse(expr, 0)
    return d

def check_lp(lhs, rhs):
    fl = first_letter(lhs)
    fr = first_letter(rhs)
    if fl and fr:
        return fl == fr  # True = HOLD
    return True

def check_rp(lhs, rhs):
    ll = last_letter(lhs)
    lr = last_letter(rhs)
    if ll and lr:
        return ll == lr
    return True

def check_c0(lhs, rhs):
    ls = has_star(lhs)
    rs = has_star(rhs)
    if ls == rs:
        return True
    return False

def check_vars(lhs, rhs):
    ls = has_star(lhs)
    rs = has_star(rhs)
    lv = var_set(lhs)
    rv = var_set(rhs)
    if ls and rs:
        return lv == rv
    elif not ls and not rs:
        return lv == rv
    elif not ls:
        v = lv
        return rv == v
    else:
        v = rv
        return lv == v

def check_count2(lhs, rhs):
    lc = var_counts(lhs)
    rc = var_counts(rhs)
    all_vars = set(lc.keys()) | set(rc.keys())
    for v in all_vars:
        if lc.get(v, 0) % 2 != rc.get(v, 0) % 2:
            return False
    return True

def check_separation(e1_hold, e2_hold):
    """Returns True if there IS separation (E1=HOLD, E2=FAIL)"""
    return e1_hold and not e2_hold

print("=== Hard2 FALSE: full separator analysis ===")
print(f"{'ID':12s} {'nv':3s} {'LP':4s} {'RP':4s} {'C0':4s} {'VAR':4s} {'CT2':4s} {'LD':4s} {'T3R':4s} {'T3L':4s} {'T5B':4s} {'NL1':4s} {'any':4s}")
print("-" * 65)

sep_count = 0
for d in false_probs:
    pid = d.get('id', '?')
    e1 = d['equation1']
    e2 = d['equation2']
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    
    mapping = assign_vars(e1, e2)
    nvars = len(mapping)
    
    results = {}
    
    # Structural tests
    for name, check_fn in [('LP', check_lp), ('RP', check_rp), ('C0', check_c0), 
                            ('VAR', check_vars), ('CT2', check_count2)]:
        e1_hold = check_fn(lhs1, rhs1)
        e2_hold = check_fn(lhs2, rhs2)
        results[name] = 'SEP' if check_separation(e1_hold, e2_hold) else '  -'
    
    # LDEPTH
    e1_lp = check_lp(lhs1, rhs1)
    e2_lp = check_lp(lhs2, rhs2)
    if e1_lp:
        e1_ld_l = count_star_depth_left(lhs1)
        e1_ld_r = count_star_depth_left(rhs1)
        e1_ld_hold = (e1_ld_l % 2 == e1_ld_r % 2)
    else:
        e1_ld_hold = False  # LP=FAIL → LDEPTH=FAIL
    if e2_lp:
        e2_ld_l = count_star_depth_left(lhs2)
        e2_ld_r = count_star_depth_left(rhs2)
        e2_ld_hold = (e2_ld_l % 2 == e2_ld_r % 2)
    else:
        e2_ld_hold = False
    results['LD'] = 'SEP' if check_separation(e1_ld_hold, e2_ld_hold) else '  -'
    
    # Magma tests
    for name, fn in [('T3R', t3r), ('T3L', t3l), ('T5B', t5b), ('NL1', nl1)]:
        if name in ('T5B', 'NL1') and nvars >= 4:
            results[name] = 'SKP'
            continue
        
        l1 = eval_magma(rewrite(lhs1, mapping), fn)
        r1 = eval_magma(rewrite(rhs1, mapping), fn)
        l2 = eval_magma(rewrite(lhs2, mapping), fn)
        r2 = eval_magma(rewrite(rhs2, mapping), fn)
        
        e1_holds = (l1 == r1)
        e2_holds = (l2 == r2)
        
        zero_map = {v: 0 for v in mapping}
        l1z = eval_magma(rewrite(lhs1, zero_map), fn)
        r1z = eval_magma(rewrite(rhs1, zero_map), fn)
        e1_holds_zero = (l1z == r1z)
        
        sep = e1_holds and e1_holds_zero and not e2_holds
        results[name] = 'SEP' if sep else '  -'
    
    any_sep = 'YES' if any(v == 'SEP' for v in results.values()) else ' NO'
    if any_sep == 'YES':
        sep_count += 1
    
    print(f"{pid:12s} {nvars:3d} {results['LP']:4s} {results['RP']:4s} {results['C0']:4s} {results['VAR']:4s} {results['CT2']:4s} {results['LD']:4s} {results['T3R']:4s} {results['T3L']:4s} {results['T5B']:4s} {results['NL1']:4s} {any_sep}")

print(f"\n{sep_count}/{len(false_probs)} FALSE problems separable by current test suite")
print(f"Theoretical max FALSE acc: {sep_count}/{len(false_probs)} = {sep_count/len(false_probs)*100:.0f}%")
print(f"Theoretical max overall (all 15 TRUE correct): {(15+sep_count)}/30 = {(15+sep_count)/30*100:.1f}%")

# Also check the TRUE problems for FN risk (magma tests saying FALSE when shouldn't)
true_probs = [d for d in data if d['answer']]
print(f"\n=== Hard2 TRUE: FN risk analysis ===")
fn_risk = 0
for d in true_probs:
    pid = d.get('id', '?')
    e1 = d['equation1']
    e2 = d['equation2']
    lhs1, rhs1 = e1.split(' = ', 1)
    lhs2, rhs2 = e2.split(' = ', 1)
    mapping = assign_vars(e1, e2)
    nvars = len(mapping)
    
    # Check structural tests for spurious separation
    risks = []
    for name, check_fn in [('LP', check_lp), ('RP', check_rp), ('C0', check_c0),
                            ('VAR', check_vars), ('CT2', check_count2)]:
        e1_hold = check_fn(lhs1, rhs1)
        e2_hold = check_fn(lhs2, rhs2)
        if check_separation(e1_hold, e2_hold):
            risks.append(name)
    
    if risks:
        fn_risk += 1
        print(f"  RISK {pid}: structural sep by {risks} — but gt=TRUE!")

if fn_risk == 0:
    print("  No structural FN risks detected")
