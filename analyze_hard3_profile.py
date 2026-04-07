"""Quick analysis of hard3 FALSE pairs structural profile."""
import json, re

with open("data/benchmark/hard3_balanced40_true20_false20_rotation0002_20260403_185904.jsonl") as f:
    lines = [json.loads(l) for l in f]

false_pairs = [l for l in lines if l["answer"] is False]

def first_letter(s):
    m = re.search(r"[a-z]", s)
    return m.group() if m else "?"

def last_letter(s):
    m = re.search(r"[a-z](?=[^a-z]*$)", s)
    return m.group() if m else "?"

def has_star(s):
    return "*" in s

def varset(s):
    return set(re.findall(r"[a-z]", s))

def left_depth(s):
    """Count opening ( before first letter, +1 if has *. Bare var=0."""
    if "*" not in s:
        return 0
    m = re.search(r"[a-z]", s)
    prefix = s[:m.start()]
    return prefix.count("(") + 1

print("=== HARD3 FALSE PAIRS: STRUCTURAL PROFILE ===")
print()
for p in false_pairs:
    pid = p["id"]
    e1, e2 = p["equation1"], p["equation2"]
    e1l, e1r = e1.split("=", 1)
    e2l, e2r = e2.split("=", 1)

    sep = []
    # LP
    if first_letter(e1l) == first_letter(e1r) and first_letter(e2l) != first_letter(e2r):
        sep.append("LP")
    # RP
    if last_letter(e1l) == last_letter(e1r) and last_letter(e2l) != last_letter(e2r):
        sep.append("RP")
    # C0
    if (has_star(e1l) == has_star(e1r)) and (has_star(e2l) != has_star(e2r)):
        sep.append("C0")
    # VARS
    if varset(e1l) == varset(e1r) and varset(e2l) != varset(e2r):
        sep.append("VARS")
    # L3 (left depth mod 3)
    if first_letter(e1l) == first_letter(e1r):
        ld1 = left_depth(e1l) % 3 == left_depth(e1r) % 3
    else:
        ld1 = False
    if first_letter(e2l) == first_letter(e2r):
        ld2 = left_depth(e2l) % 3 == left_depth(e2r) % 3
    else:
        ld2 = False
    if ld1 and not ld2:
        sep.append("L3")

    # Key structural features
    e1_vars = len(varset(e1l) | varset(e1r))
    e2_vars = len(varset(e2l) | varset(e2r))
    e1_stars = e1.count("*")
    e2_stars = e2.count("*")

    tag = ",".join(sep) if sep else "NONE"
    print(f"{pid}: [{tag:8s}] vars={e1_vars}/{e2_vars} ops={e1_stars}/{e2_stars}")
    print(f"  E1: {e1}")
    print(f"  E2: {e2}")
    print()

none_count = sum(1 for p in false_pairs
    if not any([
        first_letter(p["equation1"].split("=",1)[0]) == first_letter(p["equation1"].split("=",1)[1]) and first_letter(p["equation2"].split("=",1)[0]) != first_letter(p["equation2"].split("=",1)[1]),
        last_letter(p["equation1"].split("=",1)[0]) == last_letter(p["equation1"].split("=",1)[1]) and last_letter(p["equation2"].split("=",1)[0]) != last_letter(p["equation2"].split("=",1)[1]),
        (has_star(p["equation1"].split("=",1)[0]) == has_star(p["equation1"].split("=",1)[1])) and (has_star(p["equation2"].split("=",1)[0]) != has_star(p["equation2"].split("=",1)[1])),
    ]))

print(f"\n=== SUMMARY ===")
print(f"Total FALSE: {len(false_pairs)}")
print(f"Structurally unseparable (no LP/RP/C0): {none_count}/{len(false_pairs)}")
