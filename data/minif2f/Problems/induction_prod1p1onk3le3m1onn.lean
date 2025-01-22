import Mathlib

theorem induction_prod1p1onk3le3m1onn
  (n : ℕ)
  (h₀ : 0 < n) :
  ∏ k in Finset.range n, (1 + 1 / (k + 1)^3 : ℝ) ≤ 3 - 1 / n := by
  sorry
