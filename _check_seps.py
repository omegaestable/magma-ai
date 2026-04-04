from v21_verify_structural_rules import rule_LP, rule_RP, rule_C0, rule_AND
pairs = [
    # seed2 FP
    ("x = ((y * y) * (x * x)) * y", "x = y * (z * ((z * y) * w))"),
    ("x = ((x * (y * x)) * x) * z", "x = (x * (y * (z * y))) * w"),
    # seed0 FP  
    ("x = ((y * z) * (x * z)) * y", "x * y = (z * (w * y)) * z"),
    ("x = y * (((y * x) * z) * z)", "x = y * ((z * y) * (w * u))"),
]
for eq1, eq2 in pairs:
    l1, r1 = eq1.split(" = ", 1)
    l2, r2 = eq2.split(" = ", 1)
    seps = []
    for n, fn in [("LP", rule_LP), ("RP", rule_RP), ("C0", rule_C0), ("VARS", rule_AND)]:
        e1 = fn(l1, r1)
        e2 = fn(l2, r2)
        if e1 and not e2:
            seps.append(n)
    print(f"  {eq1[:45]:45s} -> {seps or 'COVERAGE GAP'}")
