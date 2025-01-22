import Mathlib

theorem imo_1966_p4
  (n : ℕ)
  (x : ℝ)
  (h₀ : ∀ k : ℕ, k ≤ n → ∀ m : ℤ, x ≠ m * (π : ℝ) / (2^k))
  (h₁ : 0 < n) :
  ∑ k in Finset.Icc 1 n, (1 / Real.sin ((2^k) * x)) = 1 / Real.tan x - 1 / Real.tan ((2^n) * x) := by
  sorry
