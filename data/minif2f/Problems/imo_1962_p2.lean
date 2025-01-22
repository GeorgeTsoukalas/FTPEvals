import Mathlib

theorem imo_1962_p2
  (x : ℝ)
  (h₀ : x ≤ 3)
  (h₁ : -1 ≤ x)
  (h₂ : 0 ≤ Real.sqrt (3 - x) - Real.sqrt (x + 1))
  (h₃ : Real.sqrt (Real.sqrt (3 - x) - Real.sqrt (x + 1)) > 1 / 2) :
  -1 ≤ x ∧ x < 1 - Real.sqrt 127 / 32 := by
  sorry
