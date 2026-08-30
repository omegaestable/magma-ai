import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | K : submission.M
  | E : submission.M → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def sz : M → Nat
  | .g _ => 1
  | .K => 1
  | .E t => sz t + 1
  | .J a b => sz a + sz b + 1

def tg : M → Nat
  | .g _ => 0
  | .K => 1
  | .E _ => 2
  | .J _ _ => 3
def d : M → M
  | .E t => t
  | t => t
def a1 : M → M
  | .J a _ => a
  | t => t
def a2 : M → M
  | .J _ b => b
  | t => t

@[simp] theorem tg_K : tg K = 1 := rfl
@[simp] theorem tg_E (t : M) : tg (E t) = 2 := rfl
@[simp] theorem tg_J_eq (a b : M) : tg (J a b) = 3 := rfl
@[simp] theorem d_E (t : M) : d (E t) = t := rfl
@[simp] theorem a1_J (a b : M) : a1 (J a b) = a := rfl
@[simp] theorem a2_J (a b : M) : a2 (J a b) = b := rfl
@[simp] theorem sz_E (t : M) : sz (E t) = sz t + 1 := rfl
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl

theorem sz_pos (t : M) : 0 < sz t := by cases t <;> simp [sz] <;> omega
theorem sz_d (t : M) : sz (d t) ≤ sz t := by cases t <;> simp [d, sz] <;> omega
theorem sz_a1 (t : M) : sz (a1 t) ≤ sz t := by cases t <;> simp [a1, sz] <;> omega
theorem sz_a2 (t : M) : sz (a2 t) ≤ sz t := by cases t <;> simp [a2, sz] <;> omega

/-- the seven-rule normal-form product.  Every recursive call is on a proper subterm of `v`,
    so the definition is well founded on `sz v`. -/
def op (u v : M) : M :=
  let w := d v
  let p := a1 w
  let q := a2 w
  let e := a2 (d u)
  let r1 := if h : sz q < sz v then op u q else v
  let r2 := if h : sz q < sz v then op p q else v
  let r3 := if h : sz w < sz v then op K w else v
  let r4 := if h : sz w < sz v then op u w else v
  let r5 := if h : sz e < sz v then op K e else v
  if u = v then K
  else if tg v = 1 then E u
  else if tg v = 2 ∧ ¬ (u = K) ∧ tg w = 2 ∧ d w = E u then K
  else if tg v = 2 ∧ tg w = 3 ∧ ¬ (q = K) ∧ r1 = p ∧ r2 = J p q then q
  else if tg v = 2 ∧ ¬ (w = K) ∧ u = E (J r3 w) then u
  else if tg v = 2 ∧ w = u ∧ tg u = 2 ∧ tg (d u) = 3 ∧ ¬ (e = K) ∧ r5 = a1 (d u) then E e
  else if tg v = 2 ∧ ¬ (w = K) ∧ r4 = K ∧ r3 = J K w then E (J K w)
  else J u v
termination_by sz v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption

def inst : Magma M := { op := op }

/-- goal 28770 : x = (((y ◇ y) ◇ y) ◇ x) ◇ (y ◇ z) fails at x = y = z = g 0. -/
theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (op (op (op (g 0) (g 0)) (g 0)) (g 0)) (g 0)) (g 0)
  simp (config := {decide := true}) [op.eq_1, sz, tg, d, a1, a2]

theorem law (x y z : M) : op y (op (op (op y x) x) (op z z)) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
