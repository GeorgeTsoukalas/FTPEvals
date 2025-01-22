import Mathlib

theorem aime_1994_p3
  (f : ℝ → ℝ)
  (h : ∀ x, f x + f (x - 1) = x^2)
  (h₁ : f 19 = 94) :
  ∃ n : ℤ, f 94 = n ∧ n % 1000 = 561 := by
  sorry
