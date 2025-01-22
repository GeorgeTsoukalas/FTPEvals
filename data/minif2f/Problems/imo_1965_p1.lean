import Mathlib

theorem imo_1965_p1
  (S : Set ℝ)
  (f : ℝ → ℝ)
  (h₀ : f = fun x => Real.sqrt (1 + Real.sin (2 * x)) - Real.sqrt (1 - Real.sin (2 * x)))
  (h₁ : S = {x | 0 ≤ x ∧ x ≤ 2 * Real.pi ∧ 2 * Real.cos x ≤ abs (f x) ∧ abs (f x) ≤ Real.sqrt 2}) :
  ∀ x, x ∈ S ↔ Real.pi / 4 ≤ x ∧ x ≤ 7 * Real.pi / 4 := by
  sorry
