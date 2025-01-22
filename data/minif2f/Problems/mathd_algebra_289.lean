import Mathlib

theorem mathd_algebra_289
  (f : ℝ → ℝ → ℝ → ℝ)
  (h₀ : f = fun m n x ↦ x^2 - m * x + n) 
  (m n k t : ℕ)
  (h₁ : Nat.Prime m)
  (h₂ : Nat.Prime n)
  (h₃ : k > t)
  (h₄ : f m n k = 0)
  (h₅ : f m n t = 0) :
  m^n + n^m + k^t + t^k = 20 := by
  sorry
