import Mathlib

theorem imo_1985_p6 (x : ℝ → ℕ+ → ℝ)
  (h₀ : ∀ a, x a 1 = a)
  (h₁ : ∀ a n, x a (n + 1) = x a n * (x a n + 1 / n)) :
  ∃! a, ∀ n, 0 < x a n ∧ x a n < x a (n + 1) ∧ x a (n + 1) < 1 := by
  sorry
