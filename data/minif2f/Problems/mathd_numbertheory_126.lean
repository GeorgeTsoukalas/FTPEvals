import Mathlib

theorem mathd_numbertheory_126
  (y : ℕ)
  (hy : y = 40) :
  IsLeast {z : ℕ | ∃ x > 0, Nat.gcd y z = x + 3 ∧ Nat.lcm y z = x * (x + 3)} 8 := by
  sorry
