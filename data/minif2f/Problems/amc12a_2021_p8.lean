import Mathlib

theorem amc12a_2021_p8
  (D : ℕ → ℕ)
  (h₀ : D 0 = 0)
  (h₁ : D 1 = 0)
  (h₂ : D 2 = 1)
  (h₃ : ∀ n, D (n + 3) = D (n + 2) + D n) :
  Even (D 2021) ∧ Odd (D 2022) ∧ Even (D 2023) := by
  sorry
