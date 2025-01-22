import Mathlib

theorem mathd_algebra_480
  (f : ℝ → ℝ)
  (h₀ : ∀ x, x < 0 → f x = -x^2 - 1)
  (h₁ : ∀ x, 0 ≤ x ∧ x < 4 → f x = 2)
  (h₂ : ∀ x, 4 ≤ x → f x = Real.sqrt x) :
  f Real.pi = 2 := by
  sorry
