import Mathlib

theorem mathd_numbertheory_135
  (n : ℕ)
  (A B C : ℕ)
  (h₀ : n = 3^17 + 3^10)
  (h₁ : 11 ∣ n + 1)
  (h₂ : Nat.digits 10 n = [B, A, B, C, C, A, C, B, A])
  (h₃ : A ≠ B ∧ A ≠ C ∧ B ≠ C)
  (h₄ : Odd A ∧ Odd C)
  (h₅ : ¬ (3 ∣ B)) :
  100 * A + 10 * B + C = 129 := by
  sorry
