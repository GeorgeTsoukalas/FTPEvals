import Mathlib

theorem mathd_algebra_214
  (a b c : ℝ)
  (f : ℝ → ℝ)
  (hf : ∀ x, f x = a * x^2 + b * x + c)
  (h₀ : f 2 = 3)
  (h₁ : ∀ x, f (2 + x) = f (2 - x))
  (h₂ : f 4 = 4) :
  f 6 = 7 := by
  sorry
