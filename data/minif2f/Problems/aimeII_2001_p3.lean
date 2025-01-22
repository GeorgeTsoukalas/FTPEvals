import Mathlib

theorem aimeII_2001_p3
  (x : ℕ → ℤ)
  (h₀ : x 0 = 211)
  (h₁ : x 1 = 375)
  (h₂ : x 2 = 420)
  (h₃ : x 3 = 523)
  (h₄ : ∀ n, x (n + 4) = x (n + 3) - x (n + 2) + x (n + 1) - x n) :
  x 530 + x 752 + x 974 = 898 := by
  sorry
