import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | S : submission.M → submission.M
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .S _ => 0
  | .g _ => 1
  | .J _ _ => 2

def a1 : M → M
  | .S x => x
  | .J x _ => x
  | t => t

def a2 : M → M
  | .J _ x => x
  | t => t

def sz : M → Nat
  | .g _ => 1
  | .S b0 => sz b0 + 1
  | .J b0 b1 => sz b0 + sz b1 + 1

def op (u v : M) : M :=
  if u = v then (M.S u) else if tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 v) = 0 ∧ u = (a1 (a2 v)) then (a1 (a1 v)) else M.J u v

def inst : Magma M := { op := op }

theorem eqf (a b : M) (h : sz a ≠ sz b) : (a = b) = False := eq_false (fun e => h (congrArg sz e))

theorem tg_S (t : M) (h : tg t = 0) : ∃ b0, t = M.S b0 := by cases t <;> simp_all [tg]
theorem tg_g (t : M) (h : tg t = 1) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]
theorem tg_J (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem tg_range (t : M) : tg t < 3 := by cases t <;> simp [tg]
@[simp] theorem tg_S_eq (b0 : M) : tg (M.S b0) = 0 := rfl
@[simp] theorem a1_S_eq (b0 : M) : a1 (M.S b0) = b0 := rfl
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl

theorem law (x y z : M) : (op y (op (op x (op z x)) (op y y))) = x := by
 by_cases h1 : z = x
 ·
  subst z
  simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
 ·
  by_cases h4 : tg x = 2
  ·
   obtain ⟨v2, v3, rfl⟩ := tg_J _ h4
   by_cases h7 : tg v2 = 2
   ·
    obtain ⟨v5, v6, rfl⟩ := tg_J _ h7
    by_cases h9 : tg v3 = 0
    ·
     obtain ⟨v8, rfl⟩ := tg_S _ h9
     by_cases h10 : z = v8
     ·
      subst z
      by_cases h13 : tg v5 = 2
      ·
       obtain ⟨v11, v12, rfl⟩ := tg_J _ h13
       by_cases h16 : tg v11 = 2
       ·
        obtain ⟨v14, v15, rfl⟩ := tg_J _ h16
        by_cases h18 : tg v12 = 0
        ·
         obtain ⟨v17, rfl⟩ := tg_S _ h18
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
        ·
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
       ·
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
      ·
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
     ·
      by_cases h21 : tg z = 2
      ·
       obtain ⟨v19, v20, rfl⟩ := tg_J _ h21
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1, Ne.symm h10]
      ·
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1, Ne.symm h10]
    ·
     by_cases h24 : tg z = 2
     ·
      obtain ⟨v22, v23, rfl⟩ := tg_J _ h24
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
     ·
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
   ·
    by_cases h27 : tg z = 2
    ·
     obtain ⟨v25, v26, rfl⟩ := tg_J _ h27
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
    ·
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
  ·
   by_cases h30 : tg z = 2
   ·
    obtain ⟨v28, v29, rfl⟩ := tg_J _ h30
    by_cases h32 : tg x = 0
    ·
     obtain ⟨v31, rfl⟩ := tg_S _ h32
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
    ·
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]
   ·
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h1]

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  exact absurd (h (M.g 0) (M.g 1) (M.g 2)) (by decide)

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
