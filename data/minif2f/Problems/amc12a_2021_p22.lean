import Mathlib

theorem amc12a_2021_p22
  (P : Cubic ℝ)
  (a b c : ℝ)
  (hP : P = .mk 1 a b c)
  (hRoots : P.roots = {Real.cos (2 * Real.pi / 7), Real.cos (4 * Real.pi / 7), Real.cos (6 * Real.pi / 7)}) :
  a * b * c = 1 / 32 := by
  sorry
