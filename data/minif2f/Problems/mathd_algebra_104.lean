import Mathlib

theorem mathd_algebra_104
  (calories : ℝ → ℝ)
  (h₀ : calories 8 = 125)
  (h₁ : ∀ x y, 0 < x → 0 < y → calories x / x = calories y / y) :
  calories 12 = 187.5 := by
  sorry
