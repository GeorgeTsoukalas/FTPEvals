import Mathlib

theorem amc12a_2020_p25
  (a : ℚ)
  (S : Finset ℝ)
  (h₀ : 0 < a)
  (h₁ : ∀ x, x ∈ S ↔ ⌊x⌋ * Int.fract x = a * x^2)
  (h₂ : ∑ x in S, x = 420) :
  a.num + a.den = 929 := by
  sorry
