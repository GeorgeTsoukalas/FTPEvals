import Mathlib

theorem mathd_algebra_44
  (s t : ℝ → ℝ)
  (x : ℝ × ℝ)
  (h₀ : s = fun t => 9 - 2 * t)
  (h₁ : t = fun s => 3 * s + 1)
  (h₂ : s x.2 = x.1)
  (h₂ : t x.1 = x.2) :
  x = (1, 4) := by
  sorry
