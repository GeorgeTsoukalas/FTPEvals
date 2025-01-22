import Mathlib

theorem mathd_numbertheory_435 :
  IsLeast {k : ℕ | 0 < k ∧ ∀ n > 0, Nat.Coprime (6 * n + k) (6 * n + 3) ∧ Nat.Coprime (6 * n + k) (6 * n + 2) ∧ Nat.Coprime (6 * n + k) (6 * n + 1)} 5 := by
  sorry
