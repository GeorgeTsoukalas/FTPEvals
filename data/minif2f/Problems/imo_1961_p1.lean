import Mathlib

theorem imo_1961_p1
  (a b : ℝ) :
  (∃ x y z, 0 < x ∧ 0 < y ∧ 0 < z ∧ x ≠ y ∧ y ≠ z ∧ z ≠ x ∧ x + y + z = a ∧ x^2 + y^2 + z^2 = b^2 ∧ x * y = z^2)
    ↔ |b| < a ∧ a < Real.sqrt 3 * |b| := by
  sorry
