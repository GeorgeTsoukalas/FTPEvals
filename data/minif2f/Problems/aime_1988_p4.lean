import Mathlib

theorem aime_1988_p4 :
  IsLeast {n | ∃ x : Fin n → ℝ, (∀ i, abs (x i) < 1) ∧ (∑ i, abs (x i) = 19 + abs (∑ i, x i))} 20 := by
  sorry
