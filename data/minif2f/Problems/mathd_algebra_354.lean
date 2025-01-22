import Mathlib

theorem mathd_algebra_354
  (seq : ℕ → ℝ)
  (hseq : ∃ a d : ℝ, seq = fun n : ℕ => a + d * n)
  (h7 : seq 7 = 30)
  (h11 : seq 11 = 60) :
  seq 21 = 135 := by
  sorry
