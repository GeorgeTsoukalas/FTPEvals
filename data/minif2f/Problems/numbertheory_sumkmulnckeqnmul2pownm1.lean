import Mathlib

theorem numbertheory_sumkmulnckeqnmul2pownm1
  (n k : ℕ)
  (h₀ : 0 < n) :
  ∑ k in Finset.Icc 1 n, (k * Nat.choose n k) = n * 2^(n - 1) := by
  sorry
