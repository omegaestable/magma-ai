"""Debug the coverage analysis for hard3 problems with ALL variable assignment permutations."""
import json
import re
from itertools import permutations

# Load problems
with open("data/benchmark/hard3_balanced50_true10_false40_rotation0020_20260417_002534.jsonl") as f:
    problems = [json.loads(line) for line in f]

false_problems = [p for p in problems if p["answer"] is False or p["answer"] == "FALSE"]
print(f"Total FALSE problems: {len(false_problems)}")

# ------- AST evaluator -------
def tokenize(s):
    """Tokenize an equation side: variables, *, (, )"""
    tokens = []
    i = 0
    s = s.strip()
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c in '()*':
            tokens.append(c)
            i += 1
        elif c.isalpha():
            tokens.append(c)
            i += 1
        else:
            i += 1  # skip unknown
    return tokens

def parse_expr(tokens, pos, op_func, var_map):
    """Parse: expr = atom | atom '*' atom  (binary, right-to-left nesting for a*b*c)
       Actually the equations use explicit parens for nested ops, except possibly
       at top level for simple "x * y".
       Grammar: expr = atom ('*' expr)?
    """
    val, pos = parse_atom(tokens, pos, op_func, var_map)
    if pos < len(tokens) and tokens[pos] == '*':
        pos += 1  # skip *
        val2, pos = parse_expr(tokens, pos, op_func, var_map)
        val = op_func(val, val2)
    return val, pos

def parse_atom(tokens, pos, op_func, var_map):
    """atom = variable | '(' expr ')' """
    if pos >= len(tokens):
        raise ValueError(f"Unexpected end of tokens")
    if tokens[pos] == '(':
        pos += 1  # skip (
        val, pos = parse_expr(tokens, pos, op_func, var_map)
        if pos < len(tokens) and tokens[pos] == ')':
            pos += 1
        return val, pos
    elif tokens[pos].isalpha():
        v = tokens[pos]
        pos += 1
        return var_map[v], pos
    else:
        raise ValueError(f"Unexpected token: {tokens[pos]}")

def eval_side(s, op_func, var_map):
    """Evaluate one side of an equation using the given operation and variable map."""
    toks = tokenize(s)
    val, pos = parse_expr(toks, 0, op_func, var_map)
    return val

def check_equation(eq_str, op_func, var_map):
    """Check if equation holds under given op and variable assignment. Returns True if it holds."""
    parts = eq_str.split('=', 1)
    lhs = eval_side(parts[0], op_func, var_map)
    rhs = eval_side(parts[1], op_func, var_map)
    return lhs == rhs

# ------- Magma definitions (size 3, elements 0,1,2) -------
def make_t3r(a, b): return (b + 1) % 3
def make_t3l(a, b): return (a + 1) % 3
def make_xor(a, b): return (a + b) % 3  # additive group Z3
def make_t4a(a, b): return (2*a + b) % 3  # linear
def make_t5b(a, b): return (a + 2*b) % 3  # linear
def make_allzero(a, b): return 0
def make_sub3(a, b): return (a - b) % 3
def make_mul3(a, b): return (a * b) % 3

MAGMAS = {
    "T3R": make_t3r,
    "T3L": make_t3l,
    "XOR": make_xor,
    "T4A": make_t4a,
    "T5B": make_t5b,
    "ALLZERO": make_allzero,
    "SUB3": make_sub3,
    "MUL3": make_mul3,
}

def get_variables(eq_str):
    """Extract unique variables from equation string, preserving first-appearance order."""
    seen = set()
    result = []
    for c in eq_str:
        if c.isalpha() and c not in seen:
            seen.add(c)
            result.append(c)
    return result

def separates(eq1, eq2, op_func, var_map):
    """Check if the magma separates eq1 => eq2 by satisfying eq1 but not eq2."""
    try:
        eq1_holds = check_equation(eq1, op_func, var_map)
        eq2_holds = check_equation(eq2, op_func, var_map)
        return eq1_holds and not eq2_holds
    except Exception:
        return False

# ===== PHASE 1: Default assignment (first-appearance → 0,1,2,...) =====
print("\n===== PHASE 1: Default variable assignment =====")
for name, op in MAGMAS.items():
    count = 0
    for p in false_problems:
        combined = p["equation1"] + " " + p["equation2"]
        vars_list = get_variables(combined)
        var_map = {v: i % 3 for i, v in enumerate(vars_list)}
        if separates(p["equation1"], p["equation2"], op, var_map):
            count += 1
    print(f"  {name}: {count}/40")

# ===== PHASE 2: ALL permutations of variable assignments =====
print("\n===== PHASE 2: Best variable assignment per problem =====")
for name, op in MAGMAS.items():
    count = 0
    examples = []
    for p in false_problems:
        combined = p["equation1"] + " " + p["equation2"]
        vars_list = get_variables(combined)
        n_vars = len(vars_list)
        found = False
        # Try all possible assignments of {0,1,2} to variables
        # Each variable can independently be 0, 1, or 2
        from itertools import product
        for assignment in product(range(3), repeat=n_vars):
            var_map = dict(zip(vars_list, assignment))
            if separates(p["equation1"], p["equation2"], op, var_map):
                found = True
                if len(examples) < 3:
                    examples.append((p["id"], dict(zip(vars_list, assignment))))
                break
        if found:
            count += 1
    print(f"  {name}: {count}/40")
    for ex in examples:
        print(f"    Example: {ex[0]} with assignment {ex[1]}")

# ===== PHASE 3: Any magma separates (all assignments) =====
print("\n===== PHASE 3: Combined separation (any magma, any assignment) =====")
separated = set()
separator_details = {}
for p in false_problems:
    combined = p["equation1"] + " " + p["equation2"]
    vars_list = get_variables(combined)
    n_vars = len(vars_list)
    from itertools import product
    for name, op in MAGMAS.items():
        found = False
        for assignment in product(range(3), repeat=n_vars):
            var_map = dict(zip(vars_list, assignment))
            if separates(p["equation1"], p["equation2"], op, var_map):
                separated.add(p["id"])
                separator_details[p["id"]] = (name, dict(zip(vars_list, assignment)))
                found = True
                break
        if found:
            break

print(f"Separated by any magma (any assignment): {len(separated)}/40")
print(f"Still unseparated: {40 - len(separated)}")
print("\nSeparated problems:")
for pid in sorted(separated):
    mag, assign = separator_details[pid]
    p = next(pp for pp in false_problems if pp["id"] == pid)
    print(f"  {pid}: {mag} with {assign}")
    print(f"    E1: {p['equation1']}")
    print(f"    E2: {p['equation2']}")

# Debug first 3 false problems with T3R
print("\n===== DEBUG: First 3 FALSE problems with T3R =====")
for p in false_problems[:3]:
    combined = p["equation1"] + " " + p["equation2"]
    vars_list = get_variables(combined)
    print(f"\n  {p['id']}: {p['equation1']}  =>  {p['equation2']}")
    print(f"  Variables: {vars_list}")
    
    # Default assignment
    var_map = {v: i % 3 for i, v in enumerate(vars_list)}
    print(f"  Default map: {var_map}")
    try:
        e1_l = eval_side(p["equation1"].split("=")[0], make_t3r, var_map)
        e1_r = eval_side(p["equation1"].split("=")[1], make_t3r, var_map)
        e2_l = eval_side(p["equation2"].split("=")[0], make_t3r, var_map)
        e2_r = eval_side(p["equation2"].split("=")[1], make_t3r, var_map)
        print(f"  T3R default: E1: {e1_l}=={e1_r} ({e1_l==e1_r}), E2: {e2_l}=={e2_r} ({e2_l==e2_r})")
    except Exception as ex:
        print(f"  T3R default: ERROR: {ex}")
