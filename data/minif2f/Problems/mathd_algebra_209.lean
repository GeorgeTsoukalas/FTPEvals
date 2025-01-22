import Mathlib

theorem mathd_algebra_209
  (f h : ℝ → ℝ)
  (h₂ : h 2 = 10)
  (h₁₀ : h 10 = 1)
  (h₁ : h 1 = 2)
  (hf : Function.LeftInverse h f)
  (hf' : Function.RightInverse h f) :
  f (f 10) = 1 := by
  sorry
