import Mathlib

theorem amc12a_2009_p7
  (x : ℝ)
  (n : ℕ)
  (a : ℕ → ℝ)
  (h₀ : ∃ d, ∀ n, a n = a 0 + d * n)
  (h₁ : a 1 = 2 * x - 3)
  (h₂ : a 2 = 5 * x - 11)
  (h₃ : a 3 = 3 * x + 1)
  (h₄ : a n = 2009) :
  n = 502 := by
  sorry
