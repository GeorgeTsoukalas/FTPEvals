import Mathlib

theorem amc12b_2020_p5
  (A_wins A_losses B_wins B_losses : ℕ)
  (hA : A_wins / (A_wins + A_losses : ℝ) = 2 / 3)
  (hB : B_wins / (B_wins + B_losses : ℝ) = 5 / 8)
  (hB_more : B_wins = A_wins + 7 ∧ B_losses = A_losses + 7) :
  A_wins + A_losses = 42 := by
  sorry
