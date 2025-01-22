import Mathlib

theorem mathd_algebra_156
  (f g : ℝ → ℝ)
  (m n : ℝ)
  (h₀ : f = fun x => x^4)
  (h₁ : g = fun x => 5 * x^2 - 6)
  (h₂ : f (Real.sqrt m) = g (Real.sqrt m))
  (h₃ : f (-Real.sqrt m) = g (-Real.sqrt m))
  (h₄ : f (Real.sqrt n) = g (Real.sqrt n))
  (h₅ : f (-Real.sqrt n) = g (-Real.sqrt n))
  (h₆ : 0 < n)
  (h₇ : n < m) :
  m - n = 1 := by
  sorry
