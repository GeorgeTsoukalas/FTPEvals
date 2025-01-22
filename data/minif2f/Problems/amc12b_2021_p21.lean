import Mathlib

theorem amc12b_2021_p21
  (S : ℝ)
  (h₀ : S = ∑ᶠ x ∈ {x : ℝ | 0 < x ∧ x^(2^(Real.sqrt 2) : ℝ) = (Real.sqrt 2)^(2^x : ℝ)}, x) :
  2 ≤ S ∧ S < 6 := by
  sorry
