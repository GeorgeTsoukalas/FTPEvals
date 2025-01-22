import Mathlib

theorem algebra_amgm_prod1toneq1_sum1tongeqn
  (a : ℕ → ℝ)
  (n : ℕ)
  (h₀ : ∀ i, 0 ≤ a i)
  (h₁ : ∏ i in Finset.range n, a i = 1) :
  n ≤ ∑ i in Finset.range n, a i := by
  sorry
