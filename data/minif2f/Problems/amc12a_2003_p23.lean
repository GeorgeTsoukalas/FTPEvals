import Mathlib

theorem amc12a_2003_p23 
  (S : Finset ℕ)
  (h₀ : ∀ n, n ∈ S ↔ ∃ m, m^2 = n ∧ n ∣ ∏ i in Finset.Icc 1 9, i !) :
  S.card = 672 := by
  sorry
