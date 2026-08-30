import JudgeProblem

def submission : Goal := by
  intro G _ h
  have hlem0 : ∀ a b c d : G, (b ◇ ((a ◇ (d ◇ (b ◇ a))) ◇ (c ◇ a))) = (a ◇ (d ◇ (b ◇ a))) := by
    intro a b c d
    exact (congrArg (fun t => (b ◇ ((a ◇ (d ◇ (b ◇ a))) ◇ (c ◇ t)))) (h a b d)).trans (((h (a ◇ (d ◇ (b ◇ a))) b c).symm))
  have hlem1 : ∀ a b c : G, (c ◇ (a ◇ (b ◇ (a ◇ a)))) = a := by
    intro a b c
    exact (congrArg (fun t => (c ◇ t)) ((hlem0 a a c b).symm)).trans (((h a c (a ◇ (b ◇ (a ◇ a)))).symm))
  have hlem2 : ∀ a b : G, (b ◇ a) = (a ◇ a) := by
    intro a b
    exact (congrArg (fun t => (b ◇ t)) ((hlem1 a b (a ◇ a)).symm)).trans (((h (a ◇ a) b a).symm))
  have hlem3 : ∀ a b c : G, (a ◇ (a ◇ a)) = (c ◇ (b ◇ a)) := by
    intro a b c
    exact (congrArg (fun t => (a ◇ t)) ((hlem2 a (c ◇ (b ◇ a))).symm)).trans ((congrArg (fun t => (a ◇ ((c ◇ (b ◇ a)) ◇ t))) (h a b c)).trans (((h (c ◇ (b ◇ a)) a b).symm)))
  have hlem4 : ∀ a b c d : G, (d ◇ ((b ◇ a) ◇ (c ◇ (a ◇ (a ◇ a))))) = (b ◇ a) := by
    intro a b c d
    exact (congrArg (fun t => (d ◇ ((b ◇ a) ◇ (c ◇ t)))) (hlem3 a b d)).trans (((h (b ◇ a) d c).symm))
  have hlem5 : ∀ a b c : G, (c ◇ a) = (b ◇ a) := by
    intro a b c
    exact (congrArg (fun t => (c ◇ t)) ((hlem1 a a (b ◇ a)).symm)).trans ((hlem4 a b a c))
  intro x z y
  exact (hlem5 z y x)
