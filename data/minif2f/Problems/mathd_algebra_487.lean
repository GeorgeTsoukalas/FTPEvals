import Mathlib

theorem mathd_algebra_487
  (P Q : ℝ × ℝ)
  (h₀ : P.2 = P.1^2)
  (h₁ : Q.2 = Q.1^2)
  (h₂ : P.1 + P.2 = 1)
  (h₃ : Q.1 + Q.2 = 1)
  (h₄ : P ≠ Q) :
  Real.sqrt ((P.1 - Q.1)^2 + (P.2 - Q.2)^2) = Real.sqrt 10 := by
  sorry
