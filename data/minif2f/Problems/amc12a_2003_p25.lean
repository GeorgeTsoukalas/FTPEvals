import Mathlib

theorem amc12a_2003_p25
  (f : ℝ → ℝ → ℝ → ℝ)
  (domain : ℝ → ℝ → Set ℝ)
  (h₀ : ∀ a b, domain a b = {x | 0 ≤ a * x^2 + b * x})
  (h₁ : f = fun a b x ↦ Real.sqrt (a * x^2 + b * x)) :
  Set.Nontrivial {a | ∃ b, domain a b = f a b '' domain a b} := by
  sorry
