import Mathlib

theorem mathd_numbertheory_495 :
  IsLeast {n | ∃ a b, 0 < a ∧ 0 < b ∧ a % 10 = 2 ∧ b % 10 = 4 ∧ Nat.gcd a b = 6 ∧ Nat.lcm a b = n} 108 := by
  sorry
