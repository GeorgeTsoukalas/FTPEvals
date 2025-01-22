import Mathlib

theorem amc12a_2009_p25
  (a : ℕ → ℝ)
  (h₀ : a 0 = 1)
  (h₁ : a 1 = 1 / Real.sqrt 3)
  (h₂ : ∀ n, a (n + 2) = (a n + a (n + 1)) / (1 - a n * a (n + 1))) :
  abs (a 2008) = 0 := by
  sorry
