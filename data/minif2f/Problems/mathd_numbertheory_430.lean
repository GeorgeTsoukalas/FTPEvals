import Mathlib

theorem mathd_numbertheory_430
  (A B C : ℕ)
  (h₀ : 1 ≤ A ∧ A ≤ 9)
  (h₁ : 1 ≤ B ∧ B ≤ 9)
  (h₂ : 1 ≤ C ∧ C ≤ 9)
  (h₃ : A ≠ B)
  (h₄ : A ≠ C)
  (h₅ : B ≠ C)
  (h₆ : A + B = C)
  (h₇ : A * 11 - B = 2 * C)
  (h₈ : C * B = A * 11 + A) :
  A + B + C = 8 := by
  sorry
