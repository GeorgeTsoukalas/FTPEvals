import Mathlib

theorem mathd_algebra_149
  (f : ℝ → ℝ)
  (S : Finset ℝ)
  (h₀ : ∀ x, f x = if x < -5 then x^2 + 9 else 3 * x - 8) 
  (h₁ : ∀ x, x ∈ S ↔ f x = 10) :
  ∑ x in S, x = 6 := by
  sorry
