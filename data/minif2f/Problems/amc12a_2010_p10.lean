import Mathlib

theorem amc12a_2010_p10
  (p q d : ℝ)
  (a : ℕ → ℝ)
  (h₀ : ∀ n, a n = a 0 + n * d)
  (h₁ : a 1 = p)
  (h₂ : a 2 = 9)
  (h₃ : a 3 = 3 * p - q)
  (h₄ : a 4 = 3 * p + q) :
  a 2010 = 8041 := by
  sorry
