import Mathlib

theorem aime_1983_p3
  (roots : Set ℝ)
  (h₀ : roots = {x | x^2 + 18 * x + 30 = 2 * Real.sqrt (x^2 + 18 * x + 45)}) :
  ∏ᶠ x ∈ roots, x = 20 := by
  sorry
