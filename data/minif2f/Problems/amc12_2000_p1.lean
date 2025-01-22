import Mathlib

theorem amc12_2000_p1
  (S : Set ℕ)
  (h₁ : S = {x | ∃ (i m o : ℕ), i ≠ m ∧ m ≠ o ∧ o ≠ i ∧ i*m*o = 2001 ∧ x = i+m+o}) :
  IsGreatest S 671 := by
  sorry
