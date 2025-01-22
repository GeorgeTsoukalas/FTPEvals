import Mathlib

theorem imo_2019_p1
  (f : ℤ → ℤ)
  (h₀ : ∀ a b, f (2 * a) + 2 * f b = f (f (a + b))) :
  f = (fun x => 0) ∨ ∃ c, f = (fun x => 2 * x + c) := by
  sorry
