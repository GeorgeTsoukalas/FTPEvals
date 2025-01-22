import Mathlib

theorem amc12a_2020_p4 :
  Nat.card {n : ℕ | n ∈ Finset.Icc 1000 9999 ∧ (∀ d ∈ Nat.digits 10 n, Even d) ∧ 5 ∣ n} = 100 := by
  sorry
