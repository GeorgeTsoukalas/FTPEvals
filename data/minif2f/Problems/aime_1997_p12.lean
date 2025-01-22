import Mathlib

theorem aime_1997_p12 
  (x : ℝ)
  (h₀ : x = ∑ n in Finset.Icc (1 : ℕ) 44, Real.cos (n * 180 / Real.pi) / ∑ n in Finset.Icc (1 : ℕ) 44, Real.sin (n * 180 / Real.pi)) :
  ⌊100 * x⌋ = 241 := by
  sorry
