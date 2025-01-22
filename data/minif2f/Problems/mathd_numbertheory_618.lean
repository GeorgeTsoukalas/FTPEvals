import Mathlib

theorem mathd_numbertheory_618
  (p : ℤ → ℤ)
  (h₀ : ∀ n, p n = n^2 - n + 41) :
  IsLeast {n | 0 < n ∧ 1 < Int.gcd (p n) (p (n + 1))} 41 := by
  sorry
