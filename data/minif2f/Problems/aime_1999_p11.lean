import Mathlib

theorem aime_1999_p11
  (r : ℚ)
  (h₀ : 0 < r)
  (h₁ : r < 90)
  (h₂ : ∑ k : ℕ in Finset.Icc 1 35, Real.sin (5 * k * (Real.pi / 180)) = Real.tan (r * (Real.pi / 180))) :
  r.num + r.den = 117 := by
  sorry
