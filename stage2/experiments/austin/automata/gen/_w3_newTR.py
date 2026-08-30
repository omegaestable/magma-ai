# -*- coding: utf-8 -*-
"""Lever 1: merge the P4/P5/P6 disjuncts of TR7 into one, keyed on `op u v` itself and carrying its
size bound; then simplify SZV / SUn / SH_of, which each lose two branches."""
import os, io
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
p = os.path.join(D, 'gen', '_w3_12087_proof.lean')
t = io.open(p, encoding='utf-8').read()

new_tr = """/-- one unfold of `op`: free, or one of the seven rules fired.  The three deep rules (P4,P5,P6)
    share a single disjunct keyed on `op u v` itself, which also carries their size bound. -/
theorem TR7 (u v : M) : op u v = J u v \u2228
    (P1 u v \u2227 op u v = a2 (a1 (a1 v))) \u2228
    (P2 u v \u2227 a2 v = op (a2 (a1 (a1 v))) (a2 (a1 v)) \u2227 op u v = a2 (a1 (a1 v))) \u2228
    (P3 u v \u2227 a1 (a1 v) = op u (a1 (a2 v)) \u2227 op u v = a1 (a2 v)) \u2228
    (tg v = 2 \u2227 tg (a1 v) = 2 \u2227 sz (op u v) < sz v \u2227
      a2 v = op (op u v) (a2 (a1 v)) \u2227 a1 (a1 v) = op u (op u v)) \u2228
    (P7 u v \u2227 a1 v = op (op u (a1 (a2 v))) (a2 (a2 v)) \u2227 op u v = a1 (a2 v)) := by
  obtain \u27e8p1, p2, p3, p4, p5, p6, p7, p8, p9, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hop\u27e9 := op_cases u v
  rw [hop]
  split
  \u00b7 rename_i h; exact Or.inr (Or.inl \u27e8h, rfl\u27e9)
  \u00b7 split
    \u00b7 rename_i h1 h
      obtain \u27e8h2, hs1, he\u27e9 := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inr (Or.inl \u27e8h2, he, rfl\u27e9))
    \u00b7 split
      \u00b7 rename_i h1 h2 h
        obtain \u27e8h3, hs2, he\u27e9 := h
        rw [dif_pos hs2] at hp2; subst hp2
        exact Or.inr (Or.inr (Or.inr (Or.inl \u27e8h3, he, rfl\u27e9)))
      \u00b7 split
        \u00b7 rename_i h1 h2 h3 h
          obtain \u27e8h4, hs3, hs4, he3, he4\u27e9 := h
          rw [dif_pos hs3] at hp3; subst hp3
          rw [dif_pos hs4] at hp4; subst hp4
          refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl \u27e8h4.1, h4.2.1, ?_, he3, he4\u27e9))))
          have := sz_a1 (a1 (a1 (a2 (a1 v)))); have := sz_a1 (a1 (a2 (a1 v)))
          have := sz_a1 (a2 (a1 v)); have := sz_a2_lt h4.2.1; have := sz_a1_lt h4.1; omega
        \u00b7 split
          \u00b7 rename_i h1 h2 h3 h4 h
            obtain \u27e8h5, hs5, hs6, hs7, he5, he6, he7\u27e9 := h
            rw [dif_pos hs6] at hp6; subst hp6
            rw [dif_pos hs7] at hp7; subst hp7
            refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl \u27e8h5.1, h5.2.1, ?_, he6, he7\u27e9))))
            have := sz_a1 (a1 (a1 (a2 v))); have := sz_a1 (a1 (a2 v)); have := sz_a1 (a2 v)
            have := sz_a2_lt h5.1; omega
          \u00b7 split
            \u00b7 rename_i h1 h2 h3 h4 h5 h
              obtain \u27e8h6, hs8, hs5, hs6, hs7, he8, he5, he6, he7\u27e9 := h
              rw [dif_pos hs6] at hp6; subst hp6
              rw [dif_pos hs7] at hp7; subst hp7
              refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl \u27e8h6.1, h6.2.1, ?_, he6, he7\u27e9))))
              have := sz_a1 (a1 (a1 (a2 v))); have := sz_a1 (a1 (a2 v)); have := sz_a1 (a2 v)
              have := sz_a2_lt h6.1; omega
            \u00b7 split
              \u00b7 rename_i h1 h2 h3 h4 h5 h6 h
                obtain \u27e8h7, hs2, hs9, he\u27e9 := h
                rw [dif_pos hs2] at hp2; subst hp2
                rw [dif_pos hs9] at hp9; subst hp9
                exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr \u27e8h7, he, rfl\u27e9))))
              \u00b7 left; rfl
"""

new_szv = """/-- every rule returns a proper subterm of `v` -/
theorem SZV (u v : M) : op u v = J u v \u2228 sz (op u v) < sz v := by
  rcases TR7 u v with h | \u27e8h1, h\u27e9 | \u27e8h2, -, h\u27e9 | \u27e8h3, -, h\u27e9 | \u27e8-, -, h, -\u27e9 | \u27e8h7, -, h\u27e9
  \u00b7 exact Or.inl h
  \u00b7 right; rw [h]
    have := sz_a2_lt h1.2.2.1; have := sz_a1_lt h1.2.1; have := sz_a1_lt h1.1
    have := sz_a1 (a1 v); omega
  \u00b7 right; rw [h]
    have := sz_a2_lt h2.2.2.1; have := sz_a1_lt h2.2.1; have := sz_a1_lt h2.1
    have := sz_a1 (a1 v); omega
  \u00b7 right; rw [h]
    have := sz_a1_lt h3.2.2.1; have := sz_a2_lt h3.1; omega
  \u00b7 exact Or.inr h
  \u00b7 right; rw [h]
    have := sz_a1_lt h7.2; have := sz_a2_lt h7.1; omega
"""

new_sun = """/-- a decoded product has a strictly smaller left argument -/
theorem SUn (n : Nat) : \u2200 u v : M, sz v \u2264 n \u2192 op u v \u2260 J u v \u2192 sz u < sz v := by
  induction n with
  | zero => intro u v hn _; have := sz_pos v; omega
  | succ n ih =>
    intro u v hn hd
    have step : \u2200 Y : M, sz Y < sz v \u2192 tg v = 2 \u2192 a1 (a1 v) = op u Y \u2192 sz u < sz v := by
      intro Y hY hv hg
      by_cases hW : op u Y = J u Y
      \u00b7 rw [hW] at hg
        have := congrArg sz hg; simp only [sz_J] at this
        have := sz_a1 (a1 v); have := sz_a1_lt hv; omega
      \u00b7 have h9 := ih u Y (by omega) hW; omega
    rcases TR7 u v with h | \u27e8h1, -\u27e9 | \u27e8h2, -, -\u27e9 | \u27e8h3, hg, -\u27e9 | \u27e8hv, -, hsz, -, hg\u27e9 | \u27e8h7, hg, -\u27e9
    \u00b7 exact absurd h hd
    \u00b7 have := sz_a1 (a1 (a1 v)); have := sz_a1_lt h1.2.2.1; have := sz_a1_lt h1.2.1
      have := sz_a1_lt h1.1; rw [h1.2.2.2.1]; omega
    \u00b7 have := sz_a1 (a1 (a1 v)); have := sz_a1_lt h2.2.2.1; have := sz_a1_lt h2.2.1
      have := sz_a1_lt h2.1; rw [h2.2.2.2]; omega
    \u00b7 exact step (a1 (a2 v)) (by have := sz_a1_lt h3.2.2.1; have := sz_a2_lt h3.1; omega) h3.1 hg
    \u00b7 exact step (op u v) hsz hv hg
    \u00b7 have hv := h7.1; have ha2v := h7.2
      have hX : sz (a1 (a2 v)) < sz v := by have := sz_a1_lt ha2v; have := sz_a2_lt hv; omega
      have hZ : sz (a2 (a2 v)) < sz v := by have := sz_a2_lt ha2v; have := sz_a2_lt hv; omega
      have hA : sz (a1 v) < sz v := sz_a1_lt hv
      by_cases hW : op u (a1 (a2 v)) = J u (a1 (a2 v))
      \u00b7 by_cases hR : op (op u (a1 (a2 v))) (a2 (a2 v)) = J (op u (a1 (a2 v))) (a2 (a2 v))
        \u00b7 rw [hR, hW] at hg
          have := congrArg sz hg; simp only [sz_J] at this; omega
        \u00b7 have h9 := ih (op u (a1 (a2 v))) (a2 (a2 v)) (by omega) hR
          rw [hW] at h9; simp only [sz_J] at h9; omega
      \u00b7 have h9 := ih u (a1 (a2 v)) (by omega) hW; omega
"""

new_shof_body = """  rcases TR7 u v with h | \u27e8h1, he\u27e9 | \u27e8h2, hg, he\u27e9 | \u27e8h3, hg, he\u27e9 | \u27e8hv, hav, -, hg1, hg2\u27e9 | \u27e8h7, hg, he\u27e9
  \u00b7 exact absurd h hd
  \u00b7 refine \u27e8h1.1, Or.inl \u27e8h1.2.1, Or.inl ?_, Or.inl ?_\u27e9\u27e9
    \u00b7 rw [he, h1.2.2.2.1]; exact tgJ2 h1.2.2.1
    \u00b7 rw [he, h1.2.2.2.2.2.1, h1.2.2.2.2.2.2]; exact tgJ2 h1.2.2.2.2.1
  \u00b7 refine \u27e8h2.1, Or.inl \u27e8h2.2.1, Or.inl ?_, Or.inr ?_\u27e9\u27e9
    \u00b7 rw [he, h2.2.2.2]; exact tgJ2 h2.2.2.1
    \u00b7 rw [he]; exact hg
  \u00b7 refine \u27e8h3.1, Or.inl \u27e8h3.2.1, Or.inr ?_, Or.inl ?_\u27e9\u27e9
    \u00b7 rw [he]; exact hg
    \u00b7 rw [he, h3.2.2.2]; exact tgJ2 h3.2.2.1
  \u00b7 exact \u27e8hv, Or.inl \u27e8hav, Or.inr hg2, Or.inr hg1\u27e9\u27e9
  \u00b7 refine \u27e8h7.1, Or.inr \u27e8?_, ?_\u27e9\u27e9
    \u00b7 rw [he]; exact tgJ2 h7.2
    \u00b7 rw [he]; exact hg
"""

a = t.index('/-- one unfold of `op`'); b = t.index('/-- every rule returns a proper subterm')
t = t[:a] + new_tr + '\n' + t[b:]
a = t.index('/-- every rule returns a proper subterm'); b = t.index('/-- a `J`-shaped value at least as big')
t = t[:a] + new_szv + '\n' + t[b:]
a = t.index('/-- a decoded product has a strictly smaller left argument'); b = t.index('theorem SU {u v : M}')
t = t[:a] + new_sun + '\n' + t[b:]
a = t.index('  rcases TR7 u v with h | \u27e8h1, he\u27e9'); b = t.index('/-- injectivity of a decoded product', a)
t = t[:a] + new_shof_body + '\n' + t[b:]

io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('rewrote TR7/SZV/SUn/SH_of; proof file now', len(t.encode('utf-8')), 'bytes')
