import Mathlib

theorem amc12a_2020_p15
  (A B : Set ℂ)
  (hA : A = {z | z^3 - 8 = 0})
  (hB : B = {z | z^3 - 8 * z^2 - 8 * z + 64 = 0}) :
  IsGreatest {x | ∃ a b : ℂ, a ∈ A ∧ b ∈ B ∧ x = dist a b} (2 * Real.sqrt 21) := by
  sorry
