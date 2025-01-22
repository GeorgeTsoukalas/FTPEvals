import Mathlib

theorem mathd_algebra_77
  (a b : ℝ)
  (h₀ : a ≠ 0)
  (h₁ : b ≠ 0)
  (h₂ : Polynomial.roots (Polynomial.monomial 2 1 + Polynomial.monomial 1 a + Polynomial.C b) = {a, b}) :
  (a, b) = (1, -2) := by
  sorry
