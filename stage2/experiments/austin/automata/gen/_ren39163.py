import re, collections

t = open('gen/g39163.lean', encoding='utf-8').read()

# strip comments
t = re.sub(r'[ \t]*--[^\n]*', '', t)

RESERVED = set('''import set_option namespace open end def theorem abbrev instance attribute deriving
inductive where fun let if then else match with at by rw simp only have omega intro exact apply obtain
rcases subst split rename_i left right exfalso refine generalize try cases unfold infer_instance
termination_by decreasing_by assumption this rfl show config decide true false True False Type Prop Nat
max And Or Exists Not Iff inl inr intro elim mk inj injEq symm trans mp mpr Classical byContradiction
absurd congrArg not_or dif_pos if_pos ite dite Decidable DecidableEq Magma Goal EquationLHS EquationRHS
op inst lhs rhs law submission M g J op_cases eq_1 mul_le_mul mul_succ succ_mul lt_irrefl le_refl
linter unusedSimpArgs unusedVariables warn classDefReducibility'''.split())

ids = collections.Counter(re.findall(r"(?<![A-Za-z0-9_.'])[A-Za-z][A-Za-z0-9_']*", t))
# names already length 1 stay; drop reserved
cands = [(n, c) for n, c in ids.items() if len(n) > 1 and n not in RESERVED]
cands.sort(key=lambda x: -x[1] * (len(x[0]) - 1))

used_single = {n for n in ids if len(n) == 1} | {'M', 'J'}
pool = [ch for ch in 'CDEFGHIKLNOQRSTUVWXZfijklmorsw' if ch not in used_single]

mapping = {}
for n, c in cands:
    if not pool:
        break
    mapping[n] = pool.pop(0)

for n, new in mapping.items():
    t = re.sub(r"(?<![A-Za-z0-9_.'])%s(?![A-Za-z0-9_'])" % re.escape(n), new, t)

t = re.sub(r'\n\n+', '\n\n', t)
open('gen/h39163.lean', 'w', encoding='utf-8', newline='\n').write(t)
print('bytes:', len(t.encode('utf-8')))
print('renamed', len(mapping), 'of', len(cands))
leftover = [(n, c) for n, c in cands if n not in mapping]
leftover.sort(key=lambda x: -x[1] * (len(x[0]) - 1))
print('top unrenamed:', leftover[:25])
