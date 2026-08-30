theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
@[simp] theorem sz_J (a b : M) : sz (M.J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem a1_ne {t : M} (h : tg t = 2) : a1 t ≠ t := by
  intro hc; have := sz_a1_lt h; rw [hc] at this; omega
theorem a2_ne {t : M} (h : tg t = 2) : a2 t ≠ t := by
  intro hc; have := sz_a2_lt h; rw [hc] at this; omega

/-- the `op` body with the five nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 : M,
    p1 = (if hs1 : msr (a2 (a2 (a1 u))) (v) < msr u v then op (a2 (a2 (a1 u))) (v) else J u v) ∧
    p2 = (if hs2 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v) ∧
    p5 = (if hs5 : msr (p4) (a1 (a2 v)) < msr u v then op (p4) (a1 (a2 v)) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 u)
  else if P2 u v then a2 (a1 u)
  else if P3 u v ∧ msr (a2 (a2 (a1 u))) (v) < msr u v ∧ a1 (a2 (a1 u)) = p1 then a2 (a1 u)
  else if P4 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ a1 u = p2 ∧ a1 (a2 u) = p3 then a1 v
  else if P5 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p4) (a1 (a2 v)) < msr u v ∧ u = p5 then a1 v
  else J u v) :=
  ⟨_, _, _, _, _, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the five rules fired, with its op-guards -/
theorem D (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a2 (a1 u)) ∨
    (P2 u v ∧ op u v = a2 (a1 u)) ∨
    (P3 u v ∧ a1 (a2 (a1 u)) = op (a2 (a2 (a1 u))) v ∧ op u v = a2 (a1 u)) ∨
    (P4 u v ∧ a1 u = op (a2 u) (a1 v) ∧ a1 (a2 u) = op (a2 (a2 u)) (a2 v) ∧ op u v = a1 v) ∨
    (P5 u v ∧ u = op (op (a1 (a2 v)) (a1 v)) (a1 (a2 v)) ∧ op u v = a1 v) := by
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h; exact Or.inr (Or.inr (Or.inl ⟨h, rfl⟩))
    · split
      · rename_i h1 h2 h
        obtain ⟨q, hs, he⟩ := h
        rw [dif_pos hs] at hp1; subst hp1
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨q, he, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨q, hsa, hsb, hea, heb⟩ := h
          rw [dif_pos hsa] at hp2; rw [dif_pos hsb] at hp3
          subst hp2; subst hp3
          exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨q, hea, heb, rfl⟩))))
        · split
          · rename_i h1 h2 h3 h4 h
            obtain ⟨q, hsa, hsb, he⟩ := h
            rw [dif_pos hsa] at hp4; subst hp4
            rw [dif_pos hsb] at hp5; subst hp5
            exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr ⟨q, he, rfl⟩))))
          · left; rfl

/-- the two-branch digest: a decode is an L-read `a2 (a1 u)` off a u-shaped `u`, or an R-read `a1 v`. -/
theorem TR (u v : M) : op u v = J u v ∨
    (tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ op u v = a2 (a1 u)) ∨
    (tg v = 2 ∧ op u v = a1 v) := by
  rcases D u v with h | ⟨q, h⟩ | ⟨q, h⟩ | ⟨q, -, h⟩ | ⟨q, -, -, h⟩ | ⟨q, -, h⟩
  · exact Or.inl h
  · exact Or.inr (Or.inl ⟨q.1, q.2.1, q.2.2.1, h⟩)
  · exact Or.inr (Or.inl ⟨q.1, q.2.1, q.2.2.1, h⟩)
  · exact Or.inr (Or.inl ⟨q.1, q.2.1, q.2.2.1, h⟩)
  · exact Or.inr (Or.inr ⟨q.2.1, h⟩)
  · exact Or.inr (Or.inr ⟨q.1, h⟩)

/-- sizes: a decode is a proper subterm of one of its two arguments -/
theorem SZ (u v : M) : op u v = J u v ∨ sz (op u v) + 3 ≤ sz u ∨ sz (op u v) < sz v := by
  rcases TR u v with h | ⟨h1, h2, -, h4⟩ | ⟨h1, h2⟩
  · exact Or.inl h
  · refine Or.inr (Or.inl ?_)
    have e1 := sz_tg u h1
    have e2 := sz_tg (a1 u) h2
    have e3 := sz_pos (a1 (a1 u))
    have e4 := sz_pos (a2 u)
    rw [h4]; omega
  · exact Or.inr (Or.inr (by rw [h2]; exact sz_a1_lt h1))

/-- the max form, which is what every `msr` gate wants.  Stated from `TR`, not from `SZ`:
    `omega` cannot see through a `max` on both sides (gen/LEMMA_LIBRARY.md, `mxl`), so keep the
    `max` on one side with `Nat.le_max_*` as the only bridge. -/
theorem SZM (u v : M) : op u v = J u v ∨ sz (op u v) + 2 ≤ max (sz u) (sz v) := by
  rcases TR u v with h | ⟨h1, h2, -, h4⟩ | ⟨h1, h2⟩
  · exact Or.inl h
  · refine Or.inr ?_
    have hm := Nat.le_max_left (sz u) (sz v)
    have e1 := sz_tg u h1
    have e2 := sz_tg (a1 u) h2
    have e3 := sz_pos (a1 (a1 u))
    have e4 := sz_pos (a2 u)
    rw [h4]; omega
  · refine Or.inr ?_
    have hm := Nat.le_max_right (sz u) (sz v)
    have e := sz_tg v h1
    have e2 := sz_pos (a2 v)
    rw [h2]; omega

/-- a product that shrank below its right argument is not the free product -/
theorem NEFREE {u v : M} (h : sz (op u v) < sz v) : op u v ≠ J u v := by
  intro hc; rw [hc] at h; simp only [sz_J] at h; have := sz_pos u; omega
