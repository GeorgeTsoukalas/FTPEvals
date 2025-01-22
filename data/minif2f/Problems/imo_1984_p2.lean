import Mathlib

theorem imo_1984_p2
  (a b : ℕ)
  (ha : a = 1)
  (hb : b = 18) :
  0 < a ∧ 0 < b ∧ ¬(7 ∣ a * b * (a + b)) ∧ (7^7 : ℤ) ∣ (a + b)^7 - a^7 - b^7 := by
  sorry
