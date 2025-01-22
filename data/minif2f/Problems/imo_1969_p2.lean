import Mathlib

theorem imo_1969_p2
 (x₁ x₂ : ℝ)
 (n : ℕ)
 (a : ℕ → ℝ)
 (f : ℝ → ℝ)
 (h₀ : 0 < n)
 (h₁ : ∀ (x : ℝ), f x = ∑ i in Finset.range n, ((Real.cos (a i + x)) / (2^i)))
 (h₂ : f x₁ = 0)
 (h₃ : f x₂ = 0) :
 ∃ (m : ℤ), x₂ - x₁ = m * (π : ℝ) := by
 sorry
