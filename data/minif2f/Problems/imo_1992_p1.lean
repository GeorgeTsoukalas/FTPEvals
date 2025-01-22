import Mathlib

theorem imo_1992_p1
  (S : Set (ℤ × ℤ × ℤ))
  (h₀ : S = {p | 1 < p.1 ∧ p.1 < p.2.1 ∧ p.2.1 < p.2.2 ∧ (p.1 - 1) * (p.2.1 - 1) * (p.2.2 - 1)∣(p.1 * p.2.1 * p.2.2 - 1)}) :
  S = {(2, 4, 8), (3, 5, 15)} := by
  sorry
