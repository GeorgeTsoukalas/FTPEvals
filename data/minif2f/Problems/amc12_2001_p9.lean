import Mathlib

theorem amc12_2001_p9
  (f : ℝ → ℝ)
  (h₀ : ∀ x y, 0 < x → 0 < y → f (x * y) = f x / y)
  (h₁ : f 500 = 3) :
  f 600 = 5 / 2 := by
  sorry
