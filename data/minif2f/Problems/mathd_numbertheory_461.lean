import Mathlib

theorem mathd_numbertheory_461
  (n : ℕ)
  (h₀ : n = ((Finset.Icc 1 8).filter (fun m => Nat.Coprime m 8)).card) :
  3^n % 8 = 1 := by
  sorry
