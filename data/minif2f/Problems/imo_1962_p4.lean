import Mathlib

theorem imo_1962_p4
  (S : Set ℝ)
  (h₀ : S = {x : ℝ | (Real.cos x)^2 + (Real.cos (2 * x))^2 + (Real.cos (3 * x))^2 = 1}) :
  S = {x : ℝ | ∃ (k : ℤ), x ∈ ({(2*k + 1)*Real.pi / 2, (2*k + 1)*Real.pi / 4, (6*k + 1)*Real.pi / 6, (6*k + 5)*Real.pi / 6} : Finset ℝ)} := by
  sorry
