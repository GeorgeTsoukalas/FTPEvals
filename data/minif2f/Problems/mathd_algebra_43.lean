import Mathlib

theorem mathd_algebra_43 
  (f : (ℝ × ℝ) → ℝ)
  (a b c x₀ : ℝ)
  (h₀ : ¬ (a = 0 ∧ b = 0))
  (h₁ : ∀ x, f x = a * x.1 + b * x.2 + c)
  (h₂ : f (7, 4) = 0)
  (h₃ : f (6, 3) = 0) 
  (h₄ : f (x₀, 0) = 0) :
  x₀ = 3 := by
  sorry
