import Mathlib

theorem amc12a_2008_p8
  (surface_area : ℝ → ℝ)
  (volume : ℝ → ℝ)
  (h₀ : ∀ a, surface_area a = 6 * a^2)
  (h₁ : ∀ a, volume a = a^3)
  (a b : ℝ)
  (ha : 0 < a)
  (hb : 0 < b)
  (h₂ : volume a = 1)
  (h₃ : surface_area b = 2 * surface_area a) :
  volume b = 2 * Real.sqrt 2 := by
  sorry
