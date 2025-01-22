import Mathlib

theorem imo_1968_p5_1
  (a : ℝ)
  (f : ℝ → ℝ)
  (h₀ : 0 < a)
  (h₁ : ∀ x, f x - (f x)^2 ≥ 0 ∧ f (x + a) = 1 / 2 + Real.sqrt (f x - (f x)^2)) :
  ∃ b : ℝ, 0 < b ∧ ∀ x, f (x + b) = f x := by
  sorry
