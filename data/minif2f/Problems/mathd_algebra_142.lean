import Mathlib

theorem mathd_algebra_142
  (m b : ℝ)
  (line : ℝ → ℝ → Prop)
  (h₀ : line = fun x y ↦ y = m * x + b)
  (h₁ : line 7 (-1))
  (h₂ : line (-1) 7) :
  m + b = 5 := by
  sorry
