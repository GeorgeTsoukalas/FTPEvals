import Mathlib

theorem aime_1983_p2
  (f : ℝ → ℝ)
  (p : ℝ)
  (hp : p ∈ Set.Ioo 0 15)
  (h₀ : f = fun x => abs (x - p) + abs (x - 15) + abs (x - p - 15)) :
  IsLeast {f x | (x : ℝ) (hx : x ∈ Set.Icc p 15)} 15 := by
  sorry
