import Mathlib

theorem amc12a_2002_p21
  (a S : ℕ → ℕ)
  (h₀ : a 0 = 4)
  (h₁ : a 1 = 7)
  (h₂ : ∀ n, a (n + 2) = (a n + a (n + 1)) % 10)
  (h₃ : ∀ n, S n = ∑ k in Finset.range n, a k) :
  IsLeast {n | 10000 < S n} 1999 := by
  sorry
