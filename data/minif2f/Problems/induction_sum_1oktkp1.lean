import Mathlib

theorem induction_sum_1oktkp1 (n : ℕ) (h₀ : 0 < n) :
  ∑ k in Finset.range n, (1 / ((k + 1) * (k + 2) : ℝ)) = n / (n + 1 : ℝ) := by
  sorry
