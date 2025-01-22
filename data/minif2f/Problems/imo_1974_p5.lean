import Mathlib

theorem imo_1974_p5
  (S : Set ℝ)
  (hS : S = {a / (a + b + d) + b / (a + b + c) + c / (b + c + d) + d / (a + c + d) |
    (a : ℝ) (ha : a > 0) (b : ℝ) (hb : b > 0) (c : ℝ) (hc : c > 0) (d : ℝ) (hd : d > 0)}) :
  S = Set.Ioo 1 2 := by
  sorry
