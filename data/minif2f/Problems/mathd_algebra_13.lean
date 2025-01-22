import Mathlib

theorem mathd_algebra_13
  (A B : ℝ)
  (h : ∀ x, x ≠ 3 → x ≠ 5 → (4 * x) / (x^2 - 8 * x + 15) = A / (x - 3) + B / (x - 5)) :
  (A, B) = (-6, 10) := by sorry
