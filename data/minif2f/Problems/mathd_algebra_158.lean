import Mathlib

theorem mathd_algebra_158
  (n : ℕ)
  (hn : Even n)
  (h : ∑ k in Finset.range 5, (n + 2 * k) + 4 = ∑ i in Finset.range 8, (2 * i + 1)) :
  n = 8 := by
  sorry
