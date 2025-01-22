import Mathlib

theorem mathd_numbertheory_530 : 
  IsLeast {x : ℝ | ∃ n k : ℕ+, 5 < (n / k : ℝ) ∧ (n / k : ℝ) < 6 ∧ x = Nat.lcm n k / Nat.gcd n k} 22 := by
  sorry
