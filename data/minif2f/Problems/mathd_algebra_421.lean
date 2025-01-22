import Mathlib

theorem mathd_algebra_421
  (y₁ y₂ : ℝ → ℝ)
  (a b c d : ℝ)
  (h₀ : y₁ = fun x => x^2 + 4 * x + 6)
  (h₁ : y₂ = fun x => (1 / 2) * x^2 + x + 6)
  (h₂ : (a, b) ≠ (c, d))
  (h₃ : b = y₁ a)
  (h₄ : b = y₂ a)
  (h₅ : d = y₁ c)
  (h₆ : d = y₂ c)
  (h₇ : a ≤ c) :
  c - a = 6 := by
  sorry
