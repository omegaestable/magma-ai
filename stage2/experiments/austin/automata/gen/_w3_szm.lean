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

