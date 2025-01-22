import Mathlib

theorem aimeII_2020_p6
  (t : ℕ → ℚ)
  (ht₁ : t 1 = 20)
  (ht₂ : t 2 = 21)
  (ht : ∀ n, 3 ≤ n → t n = (5 * t (n - 1) + 1) / (25 * t (n - 2))) :
  (t 2020).num + (t 2020).den = 626 := by
  sorry
