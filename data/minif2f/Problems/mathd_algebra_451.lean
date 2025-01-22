import Mathlib

theorem mathd_algebra_451
  (f g : ℝ → ℝ)
  (h₀ : Function.LeftInverse g f)
  (h₀' : Function.RightInverse g f)
  (h₁ : g (-15) = 0)
  (h₂ : g 0 = 3)
  (h₃ : g 3 = 9)
  (h₄ : g 9 = 20) :
  f (f 9) = 0 := by
  sorry
