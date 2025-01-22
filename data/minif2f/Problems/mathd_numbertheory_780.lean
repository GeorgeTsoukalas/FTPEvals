import Mathlib

theorem mathd_numbertheory_780
  (m a : ℕ)
  (h₀ : (Nat.digits 10 m).length = 2)
  (h₁ : 6 * a ≡ 1 [MOD m])
  (h₂ : a ≡ 6 ^ 2 [MOD m]) :
  m = 43 := by
  sorry
