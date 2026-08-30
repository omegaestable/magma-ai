import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b c d : G, (((c ◇ b) ◇ b) ◇ a) = (a ◇ (b ◇ (b ◇ d))) := by
    intro a b c d
    exact (congrArg (fun t => ((t ◇ b) ◇ a)) (h c b d)).trans ((congrArg (fun t => (t ◇ a)) (h ((b ◇ (b ◇ d)) ◇ c) b d)).trans (((h a (b ◇ (b ◇ d)) c).symm)))
  have hlem1 : ∀ a b c d e : G, (a ◇ b) = (a ◇ (b ◇ (b ◇ c))) := by
    intro a b c d e
    exact (h a b (b ◇ d)).trans ((congrArg (fun t => (t ◇ a)) ((hlem0 b b e d).symm)).trans ((hlem0 a b (e ◇ b) c)))
  have hlem2 : ∀ a b c d : G, (b ◇ a) = (a ◇ b) := by
    intro a b c d
    exact (h b a c).trans ((h (a ◇ (a ◇ c)) b d).trans (((hlem1 (b ◇ (b ◇ d)) a c a a).symm).trans (((h a b d).symm))))
  have hlem3 : ∀ a b c d : G, (a ◇ (b ◇ (c ◇ b))) = (a ◇ b) := by
    intro a b c d
    exact (congrArg (fun t => (a ◇ t)) ((hlem2 b (c ◇ b) a a).symm)).trans (((hlem2 a ((c ◇ b) ◇ b) a a).symm).trans ((congrArg (fun t => ((t ◇ b) ◇ a)) (h c b d)).trans ((congrArg (fun t => (t ◇ a)) (h ((b ◇ (b ◇ d)) ◇ c) b d)).trans (((h a (b ◇ (b ◇ d)) c).symm).trans (((hlem1 a b d a a).symm))))))
  have hlem4 : ∀ a b c : G, (a ◇ b) = (a ◇ (b ◇ c)) := by
    intro a b c
    exact (hlem1 a b c a a).trans ((congrArg (fun t => (a ◇ t)) ((hlem2 b (b ◇ c) a a).symm)).trans ((congrArg (fun t => (a ◇ t)) (hlem1 (b ◇ c) b c a a)).trans ((hlem3 a (b ◇ c) b a))))
  have hlem5 : ∀ a b c d : G, (a ◇ b) = (a ◇ c) := by
    intro a b c d
    exact (hlem4 a b c).trans ((congrArg (fun t => (a ◇ t)) (h b c d)).trans (((hlem4 a (c ◇ (c ◇ d)) b).symm).trans (((hlem4 a c (c ◇ d)).symm))))
  have hlem6 : ∀ a b c d : G, (a ◇ c) = (b ◇ c) := by
    intro a b c d
    exact (h a c d).trans ((hlem5 (c ◇ (c ◇ d)) a b a).trans (((h b c d).symm)))
  have hlem7 : ∀ a b c d : G, (b ◇ d) = (c ◇ a) := by
    intro a b c d
    exact ((hlem5 b a d a).symm).trans ((hlem6 b c a a))
  intro x y z
  exact (hlem7 y x y x).trans (((hlem5 y z y x).symm))
