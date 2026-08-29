import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .g _ => 0
  | .J _ _ => 1

def a1 : M → M
  | .J x _ => x
  | t => t

def a2 : M → M
  | .J _ x => x
  | t => t

def sz : M → Nat
  | .g _ => 1
  | .J b0 b1 => sz b0 + sz b1 + 1

def op (u v : M) : M :=
  if tg u = 1 ∧ tg (a1 u) = 1 ∧ tg (a1 (a1 u)) = 1 ∧ (a1 (a1 (a1 u))) = (a2 (a1 (a1 u))) ∧ (a1 (a1 (a1 u))) = (a2 (a1 u)) ∧ (a1 (a1 (a1 u))) = (a2 u) ∧ (a1 (a1 (a1 u))) = v then (M.J (M.J (M.J (M.J (a1 (a1 (a1 u))) (a1 (a1 (a1 u)))) (a1 (a1 (a1 u)))) (a1 (a1 (a1 u)))) (a1 (a1 (a1 u)))) else if tg u = 1 ∧ tg (a1 u) = 1 ∧ tg (a1 (a1 u)) = 1 ∧ (a2 (a1 (a1 u))) = (a2 (a1 u)) ∧ (a2 (a1 (a1 u))) = v then (a2 u) else M.J u v

def inst : Magma M := { op := op }

theorem eqf (a b : M) (h : sz a ≠ sz b) : (a = b) = False := eq_false (fun e => h (congrArg sz e))

theorem tg_g (t : M) (h : tg t = 0) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]
theorem tg_J (t : M) (h : tg t = 1) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem tg_range (t : M) : tg t < 2 := by cases t <;> simp [tg]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 0 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 1 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl

theorem law (x y z : M) : (op (op (op (op (op y z) y) y) x) y) = x := by
 by_cases h3 : tg y = 1
 ·
  obtain ⟨v1, v2, rfl⟩ := tg_J _ h3
  by_cases h6 : tg v1 = 1
  ·
   obtain ⟨v4, v5, rfl⟩ := tg_J _ h6
   by_cases h9 : tg v4 = 1
   ·
    obtain ⟨v7, v8, rfl⟩ := tg_J _ h9
    by_cases h10 : z = v7
    ·
     subst z
     by_cases h11 : v7 = v8
     ·
      subst v7
      by_cases h12 : v8 = v5
      ·
       subst v8
       by_cases h13 : v5 = v2
       ·
        subst v5
        by_cases h14 : x = (J (J (J v2 v2) v2) v2)
        ·
         subst x
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
        ·
         by_cases h15 : x = v2
         ·
          subst x
          simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h14]
         ·
          simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h14, Ne.symm h15]
       ·
        by_cases h18 : tg v2 = 1
        ·
         obtain ⟨v16, v17, rfl⟩ := tg_J _ h18
         by_cases h21 : tg v16 = 1
         ·
          obtain ⟨v19, v20, rfl⟩ := tg_J _ h21
          by_cases h24 : tg v19 = 1
          ·
           obtain ⟨v22, v23, rfl⟩ := tg_J _ h24
           by_cases h25 : x = (J (J v22 v23) v20)
           ·
            subst x
            by_cases h26 : (J (J v22 v23) v20) = v17
            ·
             subst v17
             simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13]
            ·
             simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h26]
           ·
            by_cases h27 : x = v17
            ·
             subst x
             simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h25]
            ·
             simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h25, Ne.symm h27]
          ·
           by_cases h28 : x = (J v19 v20)
           ·
            subst x
            by_cases h29 : (J v19 v20) = v17
            ·
             subst v17
             simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13]
            ·
             simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h29]
           ·
            by_cases h30 : x = v17
            ·
             subst x
             simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h28]
            ·
             simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h28, Ne.symm h30]
         ·
          by_cases h31 : x = v16
          ·
           subst x
           by_cases h32 : v16 = v17
           ·
            subst v16
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13]
           ·
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h32]
          ·
           by_cases h33 : x = v17
           ·
            subst x
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h31]
           ·
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13, Ne.symm h31, Ne.symm h33]
        ·
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h13]
      ·
       by_cases h34 : x = (J (J (J v8 v8) v5) v2)
       ·
        subst x
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h12]
       ·
        by_cases h35 : x = v8
        ·
         subst x
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h12, Ne.symm h34]
        ·
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h12, Ne.symm h34, Ne.symm h35]
     ·
      by_cases h36 : x = (J (J (J v7 v8) v5) v2)
      ·
       subst x
       simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11]
      ·
       by_cases h37 : x = v7
       ·
        subst x
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11, Ne.symm h36]
       ·
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h11, Ne.symm h36, Ne.symm h37]
    ·
     by_cases h38 : z = v8
     ·
      subst z
      by_cases h39 : v8 = v5
      ·
       subst v8
       by_cases h42 : tg v2 = 1
       ·
        obtain ⟨v40, v41, rfl⟩ := tg_J _ h42
        by_cases h45 : tg v40 = 1
        ·
         obtain ⟨v43, v44, rfl⟩ := tg_J _ h45
         by_cases h48 : tg v43 = 1
         ·
          obtain ⟨v46, v47, rfl⟩ := tg_J _ h48
          by_cases h49 : x = (J (J v46 v47) v44)
          ·
           subst x
           by_cases h50 : (J (J v46 v47) v44) = v41
           ·
            subst v41
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10]
           ·
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h50]
          ·
           by_cases h51 : x = v41
           ·
            subst x
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h49]
           ·
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h49, Ne.symm h51]
         ·
          by_cases h52 : x = (J v43 v44)
          ·
           subst x
           by_cases h53 : (J v43 v44) = v41
           ·
            subst v41
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10]
           ·
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h53]
          ·
           by_cases h54 : x = v41
           ·
            subst x
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h52]
           ·
            simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h52, Ne.symm h54]
        ·
         by_cases h55 : x = v40
         ·
          subst x
          by_cases h56 : v40 = v41
          ·
           subst v40
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10]
          ·
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h56]
         ·
          by_cases h57 : x = v41
          ·
           subst x
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h55]
          ·
           simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h55, Ne.symm h57]
       ·
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10]
      ·
       by_cases h58 : x = (J (J (J v7 v8) v5) v2)
       ·
        subst x
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h39]
       ·
        by_cases h59 : x = v8
        ·
         subst x
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h39, Ne.symm h58]
        ·
         simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h39, Ne.symm h58, Ne.symm h59]
     ·
      by_cases h60 : x = (J (J (J v7 v8) v5) v2)
      ·
       subst x
       by_cases h61 : (J (J (J v7 v8) v5) v2) = z
       ·
        subst z
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h38]
       ·
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h38, Ne.symm h61]
      ·
       by_cases h62 : x = z
       ·
        subst x
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h38, Ne.symm h60]
       ·
        simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h10, Ne.symm h38, Ne.symm h60, Ne.symm h62]
   ·
    by_cases h63 : x = (J (J v4 v5) v2)
    ·
     subst x
     by_cases h64 : (J (J v4 v5) v2) = z
     ·
      subst z
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
     ·
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h64]
    ·
     by_cases h65 : x = z
     ·
      subst x
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h63]
     ·
      simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h63, Ne.symm h65]
  ·
   by_cases h66 : x = (J v1 v2)
   ·
    subst x
    by_cases h67 : (J v1 v2) = z
    ·
     subst z
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
    ·
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h67]
   ·
    by_cases h68 : x = z
    ·
     subst x
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h66]
    ·
     simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h66, Ne.symm h68]
 ·
  by_cases h69 : x = y
  ·
   subst x
   by_cases h70 : y = z
   ·
    subst y
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]
   ·
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h70]
  ·
   by_cases h71 : x = z
   ·
    subst x
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h69]
   ·
    simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *, Ne.symm h69, Ne.symm h71]

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
