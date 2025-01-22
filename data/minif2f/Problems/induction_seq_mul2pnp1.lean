import Mathlib

theorem induction_seq_mul2pnp1
  (u : ℕ → ℕ)
  (h₀ : u 0 = 0)
  (h₁ : ∀ n, u (n + 1) = 2 * u n + (n + 1)) :
  ∀ n, u n = 2^(n + 1) - (n + 2) := by
  sorry
