import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | E : submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
  | .g _ => 1
  | .E => 3
  | .J _ _ => 2
def a1 : M → M
  | .J x _ => x
  | t => t
def a2 : M → M
  | .J _ x => x
  | t => t
def sz : M → Nat
  | .g _ => 1
  | .E => 1
  | .J b0 b1 => sz b0 + sz b1 + 1
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem sz_J (b0 b1 : M) : sz (M.J b0 b1) = sz b0 + sz b1 + 1 := rfl
@[simp] theorem tg_E_eq : tg E = 3 := rfl
@[simp] theorem sz_E_eq : sz E = 1 := rfl
theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1 (u : M) : sz (a1 u) ≤ sz u := by cases u <;> simp [a1, sz] <;> omega
theorem sz_a2 (u : M) : sz (a2 u) ≤ sz u := by cases u <;> simp [a2, sz] <;> omega
theorem tg_J (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  have := sz_tg t h; have := sz_pos (a2 t); omega
theorem JnE (a b : M) : M.J a b = E → False := fun h => M.noConfusion h
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt {a b u v : M} (h : max (sz a) (sz b) ≤ max (sz u) (sz v))
    (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by
  unfold msr; have := Nat.mul_le_mul h h; omega

def P1 (u v : M) : Prop :=
  tg v = 2 ∧ a2 v = E ∧ tg (a1 v) = 2 ∧ ¬ (a1 (a1 v) = E ∧ a2 (a1 v) = E)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ a2 v = E ∧ tg u = 2 ∧ a1 u = a1 v
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance

def op (u v : M) : M :=
  let p1 := if hs1 : msr u (a1 (a1 v)) < msr u v then op u (a1 (a1 v)) else J u v
  let p2 := if hs2 : msr E (a1 v) < msr u v then op E (a1 v) else J u v
  if u = v then E
  else if P1 u v ∧ msr u (a1 (a1 v)) < msr u v ∧ a2 (a1 v) = p1 then a1 (a1 v)
  else if P2 u v ∧ msr E (a1 v) < msr u v ∧ a2 u = p2 then E
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption

def inst : Magma M := { op := fun a b => op b a }

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (g 0) (op (op (op (g 0) (op (g 0) (g 0))) (g 0)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2, P1, P2]

theorem op_cases (u v : M) : ∃ p1 p2 : M,
    p1 = (if hs1 : msr u (a1 (a1 v)) < msr u v then op u (a1 (a1 v)) else J u v) ∧
    p2 = (if hs2 : msr E (a1 v) < msr u v then op E (a1 v) else J u v) ∧
    op u v = (
  if u = v then E
  else if P1 u v ∧ msr u (a1 (a1 v)) < msr u v ∧ a2 (a1 v) = p1 then a1 (a1 v)
  else if P2 u v ∧ msr E (a1 v) < msr u v ∧ a2 u = p2 then E
  else J u v) :=
  ⟨_, _, rfl, rfl, op.eq_1 u v⟩

/-- the four-way digest: free, square, decode, self-decode. -/
theorem TR (u v : M) : op u v = J u v ∨ (u = v ∧ op u v = E)
    ∨ (P1 u v ∧ a2 (a1 v) = op u (a1 (a1 v)) ∧ op u v = a1 (a1 v))
    ∨ (P2 u v ∧ a2 u = op E (a1 v) ∧ op u v = E) := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases u v
  rw [hop]; split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h; rw [dif_pos h.2.1] at hp1; subst hp1
      exact Or.inr (Or.inr (Or.inl ⟨h.1, h.2.2, rfl⟩))
    · split
      · rename_i h; rw [dif_pos h.2.1] at hp2; subst hp2
        exact Or.inr (Or.inr (Or.inr ⟨h.1, h.2.2, rfl⟩))
      · exact Or.inl rfl

theorem SQ (u : M) : op u u = E := by
  obtain ⟨p1, p2, -, -, hop⟩ := op_cases u u
  rw [hop]; simp

/-- a product whose right argument is not `(_ * E)` is free -/
theorem WF {u v : M} (h : ¬ (tg v = 2 ∧ a2 v = E)) (h2 : ¬ (u = v)) : op u v = J u v := by
  rcases TR u v with hf | ⟨he, -⟩ | ⟨hp, -, -⟩ | ⟨hp, -, -⟩
  · exact hf
  · exact absurd he h2
  · exact absurd ⟨hp.1, hp.2.1⟩ h
  · exact absurd ⟨hp.1, hp.2.1⟩ h

theorem opEw {w : M} (h : op E w = E) : w = E := by
  rcases TR E w with hf | ⟨he, -⟩ | ⟨hp, hb, hr⟩ | ⟨hp, -, -⟩
  · rw [hf] at h; exact absurd h (fun hh => JnE _ _ hh)
  · exact he.symm
  · exfalso; rw [hr] at h; rw [h, SQ E] at hb; exact hp.2.2.2 ⟨h, hb⟩
  · exfalso; have := hp.2.2.1; simp at this

/-- FREEDOWN: `op u a` is free for every `a` strictly smaller than `a1 u`. -/
theorem FD (n : Nat) : ∀ u a : M, sz a ≤ n → sz a < sz (a1 u) → op u a = J u a := by
  induction n with
  | zero => intro u a h _; have := sz_pos a; omega
  | succ n ih =>
    intro u a hn hs
    rcases TR u a with hf | ⟨he, -⟩ | ⟨hp, hb, hr⟩ | ⟨hp, -, -⟩
    · exact hf
    · exfalso; subst he; have := sz_a1 u; omega
    · exfalso
      obtain ⟨h1, h2, h3, -⟩ := hp
      have e1 := sz_tg a h1
      have e2 := sz_tg (a1 a) h3
      have e3 := sz_a1 u
      have e4 : sz a = sz (a1 (a1 a)) + sz (a2 (a1 a)) + 3 := by rw [h2] at e1; simp at e1; omega
      have e5 := ih u (a1 (a1 a)) (by omega) (by omega)
      rw [e5] at hb
      have := congrArg sz hb; simp at this; omega
    · exfalso
      obtain ⟨h1, -, -, h4⟩ := hp
      have := sz_a1_lt h1
      rw [h4] at hs; omega

/-- `op E w = E` forces `w = E`, so a term with `a2 u = E` and `a1 u` a product is never self-coded. -/
theorem NSF {u : M} (h1 : a2 u = E) (h2 : tg (a1 u) = 2) : ¬ (a2 u = op E (a1 u)) := by
  intro h
  rw [h1] at h
  have := opEw h.symm
  rw [this] at h2; simp at h2

/-- the middle product of the law's chain is free whenever `x ≠ E`. -/
theorem FREEP (x z : M) (hx : ¬ (x = E)) : op x (op z x) = J x (op z x) := by
  rcases TR z x with hf | ⟨-, he⟩ | ⟨hp, -, hr⟩ | ⟨-, -, he⟩
  · rw [hf]
    refine WF (fun hh => hx ?_) (fun hh => ?_)
    · have := hh.2; simp at this; exact this
    · have := congrArg sz hh; simp at this; have := sz_pos z; have := sz_pos x; omega
  · rw [he]; exact WF (by simp) hx
  · rw [hr]
    obtain ⟨h1, h2, h3, -⟩ := hp
    have e2 := sz_tg (a1 x) h3
    have := sz_pos (a2 (a1 x))
    exact FD (sz (a1 (a1 x))) x (a1 (a1 x)) (Nat.le_refl _) (by omega)
  · rw [he]; exact WF (by simp) hx

theorem G1 {u v : M} (h : tg v = 2) (h2 : tg (a1 v) = 2) : msr u (a1 (a1 v)) < msr u v := by
  have e1 := sz_tg v h
  have e2 := sz_tg (a1 v) h2
  have e3 := sz_pos (a2 v)
  have e4 := sz_pos (a2 (a1 v))
  have e5 := sz_a1 (a1 v)
  refine msr_lt ?_ ?_ <;> omega

theorem G2 {u v : M} (h : tg v = 2) : msr E (a1 v) < msr u v := by
  have e1 := sz_tg v h
  have e2 := sz_pos (a2 v)
  have e3 := sz_pos u
  have e4 : sz E = 1 := rfl
  refine msr_lt ?_ ?_ <;> omega

/-- the root decode: `(a * b) * E` is the code of `a` under `z` as soon as `b = op z a`. -/
theorem ROOT {z a b : M} (hab : ¬ (a = E ∧ b = E)) (hb : b = op z a) :
    op z (J (J a b) E) = a := by
  have hz : ¬ (z = J (J a b) E) := by
    intro hh
    have e0 : sz a < sz (a1 z) := by
      rw [hh]; simp; have := sz_pos b; omega
    have e1 : op z a = J z a := FD (sz a) z a (Nat.le_refl _) e0
    rw [e1] at hb
    have e2 := congrArg sz hb
    rw [hh] at e2; simp at e2; omega
  obtain ⟨p1, p2, hp1, -, hop⟩ := op_cases z (J (J a b) E)
  have hg : msr z (a1 (a1 (J (J a b) E))) < msr z (J (J a b) E) := G1 rfl rfl
  rw [dif_pos hg] at hp1; subst hp1
  rw [hop, if_neg hz, if_pos ⟨⟨rfl, rfl, rfl, hab⟩, hg, hb⟩]
  simp

/-- the degenerate root: `z` is its own code carrier, so `(a1 z) * E` decodes to `E`. -/
theorem ROOT2 {z : M} (h1 : tg z = 2) (h2 : a2 z = op E (a1 z))
    (h3 : ¬ (a1 z = E ∧ a2 z = E)) : op z (J (a1 z) E) = E := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases z (J (a1 z) E)
  have hg2 : msr E (a1 (J (a1 z) E)) < msr z (J (a1 z) E) := G2 rfl
  rw [dif_pos hg2] at hp2; subst hp2
  rw [hop]
  split
  · rfl
  · split
    · rename_i hh
      exfalso
      have hw : tg (a1 (J (a1 z) E)) = 2 := hh.1.2.2.1
      simp only [a1_J_eq] at hw
      rw [dif_pos hh.2.1] at hp1; subst hp1
      have e0 := hh.2.2
      simp only [a1_J_eq] at e0
      have e1 : op z (a1 (a1 z)) = J z (a1 (a1 z)) :=
        FD (sz (a1 (a1 z))) z (a1 (a1 z)) (Nat.le_refl _) (sz_a1_lt hw)
      rw [e1] at e0
      have e2 := congrArg sz e0
      have e3 := sz_a2 (a1 z)
      have e4 := sz_a1 z
      simp at e2; omega
    · split
      · rfl
      · rename_i hh
        exact absurd ⟨⟨rfl, rfl, h1, rfl⟩, hg2, h2⟩ hh

theorem law (x y z : M) : op (z) (op (op (x) (op (z) (x))) (op (y) (y))) = x := by
  rw [SQ y]
  by_cases hx : x = E
  · subst hx
    by_cases hz : z = E
    · subst hz; simp only [SQ]
    · have hq : op z E = J z E := WF (by simp) hz
      rw [hq]
      rcases TR E (J z E) with hf | ⟨he, -⟩ | ⟨hp, hb, hr⟩ | ⟨hp, -, -⟩
      · rw [hf, WF (by simp) (fun hh => JnE _ _ hh)]
        exact ROOT (fun h => JnE _ _ h.2) hq.symm
      · exact absurd he.symm (fun hh => JnE _ _ hh)
      · obtain ⟨-, -, ht, hne⟩ := hp
        simp only [a1_J_eq] at ht hne hb hr
        have hw : ¬ (a1 z = E) := fun hh => hne ⟨hh, by rw [hb, hh, SQ E]⟩
        rw [hr, WF (by simp) hw]
        exact ROOT2 ht hb hne
      · exfalso; have := hp.2.2.1; simp at this
  · rw [FREEP x z hx, WF (by simp) (fun hh => JnE _ _ hh)]
    exact ROOT (fun h => hx h.1) rfl

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
