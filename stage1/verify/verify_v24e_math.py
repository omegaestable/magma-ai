"""Verify L3 computations in v24e cheatsheet examples."""

def first_letter(e):
    for c in e:
        if c.isalpha(): return c

def left_depth(e):
    if '*' not in e: return 0
    for i,c in enumerate(e):
        if c.isalpha(): return e[:i].count('(') + 1

def check(label, eq):
    L, R = [s.strip() for s in eq.split('=',1)]
    fl, fr = first_letter(L), first_letter(R)
    dl, dr = left_depth(L), left_depth(R)
    hold = fl==fr and dl%3==dr%3
    result = "HOLD" if hold else "FAIL"
    print(f"  {label}: L: first={fl} ld={dl} | R: first={fr} ld={dr} -> {result}")

print("Example C (should be all FAIL):")
check("E1", "x = (y * x) * (z * (w * y))")
check("E2", "x = ((y * x) * x) * x")

print("\nExample E (E1=HOLD, E2=FAIL):")
check("E1", "x = ((x * (x * x)) * y) * z")
check("E2", "x = x * ((y * y) * z)")

print("\nTest description examples:")
for expr in ["x", "x * y", "(x * y) * z", "((x * y) * z) * w", "x * (y * z)"]:
    print(f"  \"{expr}\" -> first={first_letter(expr)} depth={left_depth(expr)}")
