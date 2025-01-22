import Mathlib

theorem amc12a_2016_p3 
  (rem : ℝ → ℝ → ℝ) 
  (h₀ : ∀ x y, y ≠ 0 → rem x y = x - y * ⌊x / y⌋) :
  rem (3 / 8) (-2 / 5) = -1 / 40 := by
  sorry
