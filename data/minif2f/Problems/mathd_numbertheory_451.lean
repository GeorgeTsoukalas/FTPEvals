import Mathlib

theorem mathd_numbertheory_451
  (Nice : ℕ → Prop)
  (h₀ : ∀ n, Nice n ↔ ∃ m > 0, m.divisors.card = 4 ∧ ∑ d in m.divisors, d = n) :
  ∑ n in (Finset.Icc 2010 2019).filter Nice, n = 2016 := by
  sorry
