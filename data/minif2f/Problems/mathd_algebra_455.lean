import Mathlib

theorem mathd_algebra_455
  (free_throws : Fin 5 → ℕ)
  (h₀ : ∀ i < 4, free_throws (i + 1) = 2 * free_throws i)
  (h₁ : free_throws 4 = 48) :
  free_throws 0 = 3 := by
  sorry
