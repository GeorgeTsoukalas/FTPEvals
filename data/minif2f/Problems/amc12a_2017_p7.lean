import Mathlib

theorem amc12a_2017_p7
  (f : ℕ → ℕ)
  (h₀ : f 1 = 2)
  (h₁ : ∀ n, Odd n → f (n + 1) = f n + 1)
  (h₂ : ∀ n, Odd n → f (n + 2) = f n + 2) :
  f 2017 = 2018 := by
  sorry
