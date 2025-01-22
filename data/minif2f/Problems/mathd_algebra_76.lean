import Mathlib

theorem mathd_algebra_76
  (f : ℤ → ℤ)
  (h₀ : f = fun n => if Odd n then n^2 else n^2 - 4 * n - 1) :
  f (f (f (f (f 4)))) = 1 := by
  sorry
