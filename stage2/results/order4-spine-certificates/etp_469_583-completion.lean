import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b c : G, (b ◇ ((a ◇ (c ◇ a)) ◇ a)) = (a ◇ (c ◇ a)) := by
    intro a b c
    exact (congrArg (fun t => (b ◇ ((a ◇ (c ◇ a)) ◇ t))) (h a (a ◇ (c ◇ a)) c)).trans (((h (a ◇ (c ◇ a)) b a).symm))
  have hlem1 : ∀ a b c d : G, (b ◇ a) = ((a ◇ (a ◇ (d ◇ a))) ◇ a) := by
    intro a b c d
    exact (congrArg (fun t => (b ◇ t)) (h a ((a ◇ (a ◇ (d ◇ a))) ◇ (c ◇ (a ◇ (a ◇ (d ◇ a))))) d)).trans ((hlem0 (a ◇ (a ◇ (d ◇ a))) b c).trans ((congrArg (fun t => ((a ◇ (a ◇ (d ◇ a))) ◇ t)) ((h a c d).symm))))
  intro x z y
  exact (hlem1 z x x y).trans (((hlem1 z y x y).symm))
