import Mathlib

theorem amc12a_2020_p13
  (a b c : ℕ)
  (h₀ : 1 < a)
  (h₁ : 1 < b)
  (h₂ : 1 < c)
  (h₃ : ∀ N : ℝ, 0 < N → N ≠ 1 → (N * (N * N ^ (1 / c : ℝ)) ^ (1 / b : ℝ)) ^ (1 / a : ℝ) = N^(25 / 36 : ℝ)) :
  b = 3 := by
  sorry
