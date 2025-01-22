import Mathlib

theorem imo_1987_p6
  (n : ℕ)
  (f : ℕ → ℕ)
  (h₀ : 2 ≤ n)
  (h₁ : ∀ k, f k = k^2 + k + n)
  (h₂ : ∀ k : ℕ, k ≤ Real.sqrt ((n:ℝ) / 3) → Nat.Prime (f k)) :
  ∀ k ≤ n - 2, Nat.Prime (f k) := by
  sorry
