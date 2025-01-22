import Mathlib

theorem amc12a_2010_p22 
  (f : ℝ → ℝ) 
  (h₀ : ∀ x, f x = ∑ i in (Finset.Icc (1 : ℕ) 119), abs (i * x - 1)) :
  IsLeast (Set.range f) 49 := by
  sorry
