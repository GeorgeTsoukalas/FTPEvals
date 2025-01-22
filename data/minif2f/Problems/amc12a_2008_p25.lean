import Mathlib

theorem amc12a_2008_p25
  (a b : ℕ → ℝ)
  (h₀ : ∀ n, a (n + 1) = Real.sqrt 3 * a n - b n)
  (h₁ : ∀ n, b (n + 1) = Real.sqrt 3 * b n + a n)
  (h₂ : a 99 = 2)
  (h₃ : b 99 = 4) :
  a 0 + b 0 = 1 / 2^98 := by
  sorry
