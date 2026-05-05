import re

def first_letter(s):
    m = re.search(r'[a-z]', s)
    return m.group() if m else None

def left_path_depth(s):
    """Count * nodes from root to leftmost leaf, always going LEFT."""
    s = s.strip()
    depth = 0
    while True:
        # Remove outer parens if they wrap the entire expression
        while s.startswith('('):
            # Check if these parens wrap the whole thing
            d = 0
            for i, c in enumerate(s):
                if c == '(': d += 1
                elif c == ')': d -= 1
                if d == 0:
                    if i == len(s) - 1:
                        s = s[1:-1].strip()
                    break
            else:
                break
            if d != 0 or i != len(s) - 1:
                break
        # Find top-level *
        d = 0
        star_pos = -1
        for i, c in enumerate(s):
            if c == '(': d += 1
            elif c == ')': d -= 1
            elif c == '*' and d == 0:
                star_pos = i
                break  # leftmost * at top level
        if star_pos < 0:
            break  # no * found, we're at a leaf
        depth += 1
        s = s[:star_pos].strip()  # take left part
    return depth

# Test cases from cheatsheet
tests = [
    ("x", 0),
    ("x * y", 1),
    ("(x * y) * z", 2),
    ("x * (y * z)", 1),
    ("((x * y) * z) * w", 3),
]
print("Left-path-depth tests:")
for expr, expected in tests:
    got = left_path_depth(expr)
    status = "OK" if got == expected else "FAIL"
    print(f"  {expr:30s} -> {got} (expected {expected}) {status}")

# Now check normal_0642
e1 = "x = (x * ((y * y) * y)) * z"
e2 = "x * x = (x * y) * (z * x)"

e1l, e1r = e1.split(" = ", 1)
e2l, e2r = e2.split(" = ", 1)

print(f"\nnormal_0642:")
print(f"  E1_L='{e1l}' first={first_letter(e1l)} depth={left_path_depth(e1l)}")
print(f"  E1_R='{e1r}' first={first_letter(e1r)} depth={left_path_depth(e1r)}")
lp_e1 = first_letter(e1l) == first_letter(e1r)
dp_e1 = left_path_depth(e1l) % 2 == left_path_depth(e1r) % 2
ldepth_e1 = "HOLD" if lp_e1 and dp_e1 else "FAIL"
print(f"  LP_E1={'HOLD' if lp_e1 else 'FAIL'}, depth parity {'match' if dp_e1 else 'mismatch'} -> LDEPTH E1={ldepth_e1}")

print(f"  E2_L='{e2l}' first={first_letter(e2l)} depth={left_path_depth(e2l)}")
print(f"  E2_R='{e2r}' first={first_letter(e2r)} depth={left_path_depth(e2r)}")
lp_e2 = first_letter(e2l) == first_letter(e2r)
dp_e2 = left_path_depth(e2l) % 2 == left_path_depth(e2r) % 2
ldepth_e2 = "HOLD" if lp_e2 and dp_e2 else "FAIL"
print(f"  LP_E2={'HOLD' if lp_e2 else 'FAIL'}, depth parity {'match' if dp_e2 else 'mismatch'} -> LDEPTH E2={ldepth_e2}")

sep = "SEP -> FALSE" if ldepth_e1 == "HOLD" and ldepth_e2 == "FAIL" else "no sep"
print(f"  Decision: {sep}")
