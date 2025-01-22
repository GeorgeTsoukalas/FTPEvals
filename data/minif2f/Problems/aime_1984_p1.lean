import Mathlib

theorem aime_1984_p1
  (a : ℕ+ → ℤ)
  (h₀ : ∀ n, a (n + 1) = a n + 1)
  (h₁ : ∑ i in Finset.Icc 1 98, a i = 137) :
  ∑ i in ((Finset.Icc 2 98).filter (Even ·)), a i = 93 := by
  sorry
