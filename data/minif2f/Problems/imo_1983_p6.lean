import Mathlib

theorem imo_1983_p6
  (a b c d : ℝ)
  (h₀ : 0 < a ∧ 0 < b ∧ 0 < c)
  (h₁ : c < a + b)
  (h₂ : b < a + c)
  (h₃ : a < b + c) 
  (h₄ : d = a^2 * b * (a - b) + b^2 * c * (b - c) + c^2 * a * (c - a) ):
  0 ≤ d ∧ (d = 0 ↔ (a = b ∧ b = c)) := by
  sorry
