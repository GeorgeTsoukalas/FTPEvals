import Mathlib

theorem mathd_algebra_234
  (a : ℕ → ℚ)
  (h₀ : a 0 = 27 / 125)
  (h₁ : a 1 = 9 / 25)
  (h₂ : a 2 = 3 / 5)
  (h₃ : ∀ n, a (n + 1) = a n * (a 1 / a 0)) :
  a 5 = 25 / 9 := by
  sorry
