import Mathlib

theorem induction_sum_odd (n : ℕ) (h₀ : 0 < n) : ∑ k in Finset.range n, (2 * k + 1) = n^2 := by
  sorry
