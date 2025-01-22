import Mathlib

theorem mathd_algebra_440
  (water_drank : ℝ → ℝ)
  (h₀ : water_drank 3 = 1.5)
  (h₁ : ∀ x y, 0 < x → 0 < y → water_drank x / x = water_drank y / y) :
  water_drank 10 = 5 := by
  sorry
