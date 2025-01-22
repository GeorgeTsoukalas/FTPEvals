import Mathlib

theorem induction_pord1p1on2powklt5on2
  (n : ℕ)
  (hn : 0 < n) :
  ∏ k : ℕ in Finset.Icc 1 n, (1 + 1 / (2^k : ℝ)) < 5 / 2 := by
  sorry
