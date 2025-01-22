import Mathlib

theorem amc12a_2019_p9
  (a : ℕ → ℚ)
  (h₀ : a 0 = 1)
  (h₁ : a 1 = 3 / 7)
  (h₂ : ∀ n, a (n + 2) = a n * a (n + 1) / (2 * a n - a (n + 1))) :
  letI r := a 2018; r.num + r.den = 8078 := by
  sorry
