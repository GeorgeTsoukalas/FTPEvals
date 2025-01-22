import Mathlib

theorem mathd_algebra_132
  (f g : ℝ → ℝ)
  (h₀ : f = fun x => x + 2)
  (h₁ : g = fun x => x^2) :
  ∀ x, x = - 1 / 2 → f (g x) = g (f x) := by
  sorry
