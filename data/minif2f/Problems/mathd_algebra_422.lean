import Mathlib

theorem mathd_algebra_422
  (f : ℝ ≃ ℝ)
  (hf : ∀ x, f x = 5 * x - 12)
  (x : ℝ)
  (hx : x = 47 / 24) :
  f.symm x = f (x + 1) := by
  sorry
