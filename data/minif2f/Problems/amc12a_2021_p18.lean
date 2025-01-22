import Mathlib

theorem amc12a_2021_p18
  (f : ℚ → ℝ)
  (h₀ : ∀ x > 0, ∀ y > 0, f (x * y) = f x + f y)
  (h₁ : ∀ p, Nat.Prime p → f p = p) :
  f (25 / 11) < 0 := by
  sorry
