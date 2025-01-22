import Mathlib

theorem mathd_numbertheory_42
  (p : ℕ → Prop)
  (hp : p = fun a ↦ 0 < a ∧ 27 * a ≡ 17 [MOD 40]) :
  Nat.nth p 0 + Nat.nth p 1 = 62:= by
  sorry
