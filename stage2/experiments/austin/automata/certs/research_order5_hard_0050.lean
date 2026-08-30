import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | K : submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def sz : M → Nat
  | .g _ => 1
  | .K => 1
  | .J a b => sz a + sz b + 1

def tg : M → Nat
  | .g _ => 0
  | .K => 1
  | .J _ _ => 2
def a1 : M → M
  | .J a _ => a
  | t => t
def a2 : M → M
  | .J _ b => b
  | t => t

@[simp] theorem tg_J_eq (a b : M) : tg (J a b) = 2 := rfl
@[simp] theorem a1_J (a b : M) : a1 (J a b) = a := rfl
@[simp] theorem a2_J (a b : M) : a2 (J a b) = b := rfl
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_pos (t : M) : 0 < sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1 (t : M) : sz (a1 t) ≤ sz t := by cases t <;> simp [a1, sz] <;> omega
theorem sz_a2 (t : M) : sz (a2 t) ≤ sz t := by cases t <;> simp [a2, sz] <;> omega

/-- three-rule normal-form product for 27859. -/
def op (u v : M) : M :=
  let a := a1 (a1 u)
  let b := a2 (a1 u)
  let q := a2 u
  let r1 := if h : sz a + sz q < sz u + sz v then op a q else u
  let r2 := if h : sz a + sz b < sz u + sz v then op a b else u
  if u = v then K
  else if v = K ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ r1 = b ∧ r2 = J a b then q
  else if v = K ∧ tg u = 2 ∧ tg q = 2 ∧ a2 q = a1 u then q
  else J u v
termination_by sz u + sz v
decreasing_by
  · assumption
  · assumption

def inst : Magma M := { op := op }

/-- goal 4916 : x = y ◇ (x ◇ (x ◇ (y ◇ (z ◇ z)))) fails at x = y = z = g 0. -/
theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (g 0) (op (g 0) (op (g 0) (op (g 0) (op (g 0) (g 0)))))
  simp (config := {decide := true}) [op.eq_1, sz, tg, a1, a2]

theorem op_cases (u v : M) : ∃ r1 r2 : M,
    r1 = (if h : sz (a1 (a1 u)) + sz (a2 u) < sz u + sz v then op (a1 (a1 u)) (a2 u) else u) ∧
    r2 = (if h : sz (a1 (a1 u)) + sz (a2 (a1 u)) < sz u + sz v then op (a1 (a1 u)) (a2 (a1 u)) else u) ∧
    op u v = (
      if u = v then K
      else if v = K ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ r1 = a2 (a1 u) ∧
          r2 = J (a1 (a1 u)) (a2 (a1 u)) then a2 u
      else if v = K ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ a2 (a2 u) = a1 u then a2 u
      else J u v) :=
  ⟨_, _, rfl, rfl, op.eq_1 u v⟩

theorem tgJ {t : M} (h : tg t = 2) : ∃ a b, t = J a b := by
  cases t with
  | g n => simp [tg] at h
  | K => simp [tg] at h
  | J a b => exact ⟨a, b, rfl⟩

theorem szt {t : M} (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tgJ h; simp

theorem szc (t : M) : tg t = 2 ∨ (a1 t = t ∧ a2 t = t ∧ sz t = 1) := by
  cases t with
  | g n => exact Or.inr ⟨rfl, rfl, rfl⟩
  | K => exact Or.inr ⟨rfl, rfl, rfl⟩
  | J a b => exact Or.inl rfl

theorem sza2 {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tgJ h
  simp only [a2_J, sz_J]
  have := sz_pos a; omega

theorem JK (a b : M) : J a b ≠ K := by
  intro h; have := congrArg tg h; simp [tg] at this

theorem gA {u : M} (h : tg u = 2) : sz (a1 (a1 u)) + sz (a2 u) < sz u + sz K := by
  have e := szt h
  have h1 := sz_a1 (a1 u)
  show _ < sz u + 1
  omega

theorem gB {u : M} (h : tg u = 2) : sz (a1 (a1 u)) + sz (a2 (a1 u)) < sz u + sz K := by
  have e := szt h
  have h3 := sz_pos (a2 u)
  show _ < sz u + 1
  rcases szc (a1 u) with hh | ⟨e1, e2, e3⟩
  · have := szt hh; omega
  · rw [e1, e2]; omega

theorem sq (u : M) : op u u = K := by
  obtain ⟨r1, r2, -, -, hop⟩ := op_cases u u
  rw [hop, if_pos rfl]

theorem TR (u v : M) : u = v ∨ (v = K ∧ tg u = 2 ∧ op u v = a2 u) ∨ op u v = J u v := by
  obtain ⟨r1, r2, -, -, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inl h
  · split
    · rename_i h; exact Or.inr (Or.inl ⟨h.1, h.2.1, rfl⟩)
    · split
      · rename_i h; exact Or.inr (Or.inl ⟨h.1, h.2.1, rfl⟩)
      · exact Or.inr (Or.inr rfl)

theorem FR {u v : M} (h1 : u ≠ v) (h2 : v ≠ K) : op u v = J u v := by
  rcases TR u v with h | ⟨h, -, -⟩ | h
  · exact absurd h h1
  · exact absurd h h2
  · exact h

theorem RD {u : M} (h2 : tg u = 2) (h3 : tg (a1 u) = 2)
    (e1 : op (a1 (a1 u)) (a2 u) = a2 (a1 u))
    (e2 : op (a1 (a1 u)) (a2 (a1 u)) = J (a1 (a1 u)) (a2 (a1 u))) : op u K = a2 u := by
  obtain ⟨r1, r2, hr1, hr2, hop⟩ := op_cases u K
  rw [dif_pos (gA h2)] at hr1
  rw [dif_pos (gB h2)] at hr2
  subst hr1; subst hr2
  have hne : u ≠ K := by intro h; rw [h] at h2; simp [tg] at h2
  rw [hop, if_neg hne, if_pos ⟨rfl, h2, h3, e1, e2⟩]

theorem RD2 {u : M} (h2 : tg u = 2) (h3 : tg (a2 u) = 2)
    (e : a2 (a2 u) = a1 u) : op u K = a2 u := by
  obtain ⟨r1, r2, hr1, hr2, hop⟩ := op_cases u K
  rw [dif_pos (gA h2)] at hr1
  rw [dif_pos (gB h2)] at hr2
  subst hr1; subst hr2
  have hne : u ≠ K := by intro h; rw [h] at h2; simp [tg] at h2
  rw [hop, if_neg hne]
  split
  · rfl
  · rw [if_pos ⟨rfl, h2, h3, e⟩]

theorem NOFK {u : M} (h1 : u ≠ K)
    (n1 : ¬(tg (a1 u) = 2 ∧ op (a1 (a1 u)) (a2 u) = a2 (a1 u) ∧
            op (a1 (a1 u)) (a2 (a1 u)) = J (a1 (a1 u)) (a2 (a1 u))))
    (n2 : ¬(tg (a2 u) = 2 ∧ a2 (a2 u) = a1 u)) : op u K = J u K := by
  obtain ⟨r1, r2, hr1, hr2, hop⟩ := op_cases u K
  by_cases ht : tg u = 2
  · rw [dif_pos (gA ht)] at hr1
    rw [dif_pos (gB ht)] at hr2
    subst hr1; subst hr2
    rw [hop, if_neg h1, if_neg (fun k => n1 ⟨k.2.2.1, k.2.2.2.1, k.2.2.2.2⟩),
      if_neg (fun k => n2 ⟨k.2.2.1, k.2.2.2⟩)]
  · rw [hop, if_neg h1, if_neg (fun k => ht k.2.1), if_neg (fun k => ht k.2.1)]

theorem MAIN {x y : M} (hB : op y (op y x) = J y (op y x))
    (hC : op (op y (op y x)) x = J (op y (op y x)) x) :
    op (op (op y (op y x)) x) K = x := by
  rw [hC, hB]
  exact RD rfl rfl rfl hB

theorem SELF (x : M) (hx : x ≠ K) : op (op (op x (op x x)) x) K = x := by
  have hs : op x x = K := sq x
  rcases TR x K with h | ⟨-, h2, hd⟩ | hf
  · exact absurd h hx
  · have hne : a2 x ≠ x := by
      intro h; have := sza2 h2; rw [h] at this; omega
    rw [hs, hd, FR hne hx]
    exact RD2 rfl h2 rfl
  · have hB : op x (op x x) = J x (op x x) := by rw [hs]; exact hf
    have hC : op (op x (op x x)) x = J (op x (op x x)) x := by
      rw [hB, hs]
      refine FR (fun h => ?_) hx
      have := congrArg sz h; simp at this
      have := sz_pos x; omega
    exact MAIN hB hC

theorem CASEK (y : M) : op (op (op y (op y K)) K) K = K := by
  by_cases hA : op y K = K
  · simp only [hA, sq]
  · have hyA : y ≠ op y K := by
      intro h
      rcases TR y K with e | ⟨-, ht, hd⟩ | hf
      · rw [e] at hA; exact hA (sq K)
      · have := sza2 ht; rw [← hd, ← h] at this; omega
      · rw [hf] at h; have := congrArg sz h; simp at this
        have := sz_pos y; omega
    have hB : op y (op y K) = J y (op y K) := FR hyA hA
    have hC : op (op y (op y K)) K = J (op y (op y K)) K := by
      rw [hB]
      refine NOFK (JK _ _) (fun k => ?_) (fun k => ?_)
      · simp only [a1_J, a2_J] at k
        rcases TR y K with e | ⟨-, ht, hd⟩ | hf
        · rw [e] at hA; exact hA (sq K)
        · have q1 := k.2.1
          rw [hd] at q1
          have q2 := k.2.2
          rw [q1] at q2
          have := congrArg sz q2; simp at this
          have := sz_pos (a1 y); omega
        · have q1 := k.2.1
          rw [hf] at q1
          rcases TR (a1 y) (J y K) with e2 | ⟨e2, -, -⟩ | e2
          · have := congrArg sz e2; simp at this
            have := sz_a1 y; have := sz_pos y; omega
          · exact JK _ _ e2
          · rw [e2] at q1
            have := congrArg sz q1; simp at this
            have := sz_a2 y; have := sz_pos (a1 y); omega
      · simp only [a1_J, a2_J] at k
        rcases TR y K with e | ⟨-, ht, hd⟩ | hf
        · rw [e] at hA; exact hA (sq K)
        · have q := k.2
          rw [hd] at q
          have s1 := sza2 ht
          have s2 := sz_a2 (a2 y)
          have := congrArg sz q; omega
        · have q := k.2
          rw [hf] at q; simp only [a2_J] at q
          rw [← q] at hA; exact hA (sq K)
    exact MAIN hB hC

theorem law (x y z : M) : op (op (op y (op y x)) x) (op z z) = x := by
  rw [sq z]
  by_cases hx : x = K
  · subst hx; exact CASEK y
  · by_cases hyx : y = x
    · rw [hyx]; exact SELF x hx
    · have hA : op y x = J y x := FR hyx hx
      have hB : op y (op y x) = J y (op y x) := by
        rw [hA]
        refine FR (fun h => ?_) (JK _ _)
        have := congrArg sz h; simp at this
        have := sz_pos x; omega
      have hC : op (op y (op y x)) x = J (op y (op y x)) x := by
        rw [hB, hA]
        refine FR (fun h => ?_) hx
        have := congrArg sz h; simp at this
        have := sz_pos y; omega
      exact MAIN hB hC

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
