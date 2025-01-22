import Mathlib

theorem amc12_2001_p2
  (p s : ℕ → ℕ)
  (hp : p = fun n ↦ (Nat.digits 10 n).prod)
  (hs : s = fun n ↦ (Nat.digits 10 n).sum)
  (N : ℕ)
  (h₀ : (Nat.digits 10 N).length = 2)
  (h₁ : N = p N + s N) :
  N % 10 = 9 := by
  sorry
