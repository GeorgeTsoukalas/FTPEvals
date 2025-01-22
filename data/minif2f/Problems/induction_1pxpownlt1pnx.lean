import Mathlib

theorem induction_1pxpownlt1pnx
  (x : ℝ)
  (hx : -1 < x) :
  ∀ n : ℕ, (1 + n * x) ≤ (1 + x)^n := by
  sorry
