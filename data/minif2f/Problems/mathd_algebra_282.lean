import Mathlib

theorem mathd_algebra_282
  (f : ℝ → ℝ)
  (h₀ : ∀ x, f x = if Irrational x then ⌈x⌉^2 else abs (⌊x⌋))
  (a : ℝ)
  (ha : a ^ 3 = -8) :
  f a + f (-Real.pi) + f (Real.sqrt 50) + f (9 / 2) = 79 := by
  sorry
