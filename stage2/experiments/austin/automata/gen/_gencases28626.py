import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# op_cases text
lets = [
 ("p1", "msr (a2 (a2 (a1 (a1 u)))) (v)", "op (a2 (a2 (a1 (a1 u)))) (v)"),
 ("p2", "msr (p1) (a2 (a2 (a1 (a1 u))))", "op (p1) (a2 (a2 (a1 (a1 u))))"),
 ("p3", "msr (a2 (a1 (a2 (a1 (a1 u))))) (v)", "op (a2 (a1 (a2 (a1 (a1 u))))) (v)"),
 ("p4", "msr (a2 (a1 u)) (a1 v)", "op (a2 (a1 u)) (a1 v)"),
 ("p5", "msr (a2 u) (a1 v)", "op (a2 u) (a1 v)"),
 ("p6", "msr (p5) (a2 u)", "op (p5) (a2 u)"),
 ("p7", "msr (a2 u) (a1 (a1 (a2 u)))", "op (a2 u) (a1 (a1 (a2 u)))"),
 ("p8", "msr (p7) (a2 u)", "op (p7) (a2 u)"),
 ("p9", "msr (a2 (a2 u)) (a1 u)", "op (a2 (a2 u)) (a1 u)"),
 ("p10", "msr (a2 u) (a2 (a2 u))", "op (a2 u) (a2 (a2 u))"),
 ("p11", "msr (p10) (a2 u)", "op (p10) (a2 u)"),
 ("p12", "msr (a2 (a1 (a2 (a2 u)))) (v)", "op (a2 (a1 (a2 (a2 u)))) (v)"),
]

branches = [
 ("P1 u v", "a2 (a1 (a1 u))"),
 ("P2 u v", "a2 (a1 (a1 u))"),
 ("P3 u v ∧ msr (a2 (a2 (a1 (a1 u)))) (v) < msr u v ∧ msr (p1) (a2 (a2 (a1 (a1 u)))) < msr u v ∧ a1 (a2 (a1 (a1 u))) = p2", "a2 (a1 (a1 u))"),
 ("P4 u v ∧ msr (a2 (a1 (a2 (a1 (a1 u))))) (v) < msr u v ∧ a1 (a1 (a2 (a1 (a1 u)))) = p3", "a2 (a1 (a1 u))"),
 ("P5 u v ∧ msr (a2 (a1 u)) (a1 v) < msr u v ∧ a1 (a1 u) = p4", "a1 v"),
 ("P6 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (p5) (a2 u) < msr u v ∧ a1 u = p6", "a1 v"),
 ("P7 u v ∧ msr (a2 u) (a1 (a1 (a2 u))) < msr u v ∧ msr (p7) (a2 u) < msr u v ∧ a1 u = p8", "a1 (a1 (a2 u))"),
 ("P8 u v ∧ msr (a2 (a2 u)) (a1 u) < msr u v ∧ msr (a2 u) (a2 (a2 u)) < msr u v ∧ msr (p10) (a2 u) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v ∧ a1 (a2 u) = p9 ∧ a1 u = p11 ∧ a1 (a1 (a2 (a2 u))) = p12", "a2 (a2 u)"),
 ("P9 u v", "a1 (a1 (a2 u))"),
 ("P10 u v ∧ msr (a2 (a2 u)) (a1 u) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v ∧ a1 (a2 u) = p9 ∧ a1 (a1 (a2 (a2 u))) = p12", "a2 (a2 u)"),
]

out = []
out.append("theorem op_cases (u v : M) : ∃ " + " ".join(nm for nm,_,_ in lets) + " : M,")
lines = []
for nm, cond, res in lets:
    lines.append("    %s = (if hs%s : %s < msr u v then %s else J u v)" % (nm, nm[1:], cond, res))
body = " ∧\n    if ".join(["op u v = (\n  if " ])
# build if-chain
ifchain = "  if " + branches[0][0] + " then " + branches[0][1] + "\n"
for cond, res in branches[1:]:
    ifchain += "  else if " + cond + " then " + res + "\n"
ifchain += "  else J u v)"
out.append(" ∧\n".join(lines) + " ∧\n    op u v = (\n" + ifchain + " :=")
out.append("  ⟨" + ", ".join(["_"]*len(lets)) + ", " + ", ".join(["rfl"]*len(lets)) + ", op.eq_1 u v⟩")
print("\n".join(out))
