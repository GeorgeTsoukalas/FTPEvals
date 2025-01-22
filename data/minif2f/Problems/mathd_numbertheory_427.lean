import Mathlib

theorem mathd_numbertheory_427
  (A : ℕ)
  (h₀ : A = ∑ x in (500 : ℕ).divisors, x) :
  ∑ x in A.primeFactors, x = 25 := by
  sorry
