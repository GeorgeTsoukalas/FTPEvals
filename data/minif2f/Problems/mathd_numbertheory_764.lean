import Mathlib

theorem mathd_numbertheory_764
  (p : ℕ)
  (h₀ : Nat.Prime p)
  (h₁ : 7 ≤ p) :
  (∑ k : ℕ in Finset.Ico 1 (p - 1), (k : ZMod p)⁻¹ * (k + 1 : ZMod p)⁻¹) = 2 := by
  sorry
