import Mathlib

theorem amc12a_2020_p10
  (n : ℕ)
  (h₀ : 0 < n)
  (h₁ : n ≠ 1)
  (h₂ : Real.logb 2 (Real.logb 16 n) = Real.logb 4 (Real.logb 4 n)) :
  (Nat.digits 10 n).sum = 13 := by sorry
