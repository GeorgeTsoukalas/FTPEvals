import Mathlib

theorem amc12a_2019_p12
  (x y : ℝ)
  (hx : 0 < x ∧ x ≠ 1)
  (hy : 0 < y ∧ y ≠ 1)
  (h₁ : Real.logb 2 x = Real.logb y 16)
  (h₂ : x * y = 64) :
  (Real.logb 2 (x / y))^2 = 20 := by
  sorry
