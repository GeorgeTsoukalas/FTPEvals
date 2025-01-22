import Mathlib

theorem imo_2007_p6
  (a : Fin 100 → ℝ)
  (h₀ : ∀ i, 0 ≤ a i)
  (h₁ : ∑ i, a i^2 = 1) :
  ∑ i, a i^2 * a (i + 1) < 12 / 25 := by
  sorry
