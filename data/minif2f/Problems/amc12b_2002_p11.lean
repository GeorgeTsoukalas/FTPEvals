import Mathlib

theorem amc12b_2002_p11
  (A B : ℕ)
  (h₀ : 0 < B)
  (h₁ : B < A)
  (h₂ : Nat.Prime A)
  (h₃ : Nat.Prime B)
  (h₄ : Nat.Prime (A - B))
  (h₅ : Nat.Prime (A + B)) :
  Nat.Prime (A + B + (A - B) + A + B) := by
  sorry
