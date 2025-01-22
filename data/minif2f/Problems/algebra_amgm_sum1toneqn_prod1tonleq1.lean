import Mathlib

theorem algebra_amgm_sum1toneqn_prod1tonleq1
  (n : ℕ)
  (a : Fin n → ℝ)
  (h₀ : ∀ i, 0 ≤ a i)
  (h₁ : ∑ i, a i = n) :
  ∏ i, a i ≤ 1 := by
  sorry
