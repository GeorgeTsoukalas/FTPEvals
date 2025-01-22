import Mathlib

theorem aime_1995_p7
  (t : ℝ)
  (m n k : ℕ)
  (h₀ : 0 < m)
  (h₁ : 0 < n)
  (h₂ : 0 < k)
  (h₃ : (1 + Real.sin t) * (1 + Real.cos t) = 5 / 4)
  (h₄ : (1 - Real.sin t) * (1 - Real.cos t) = m / n - Real.sqrt k)
  (h₅ : Nat.Coprime m n) :
  k + m + n = 27 := by
  sorry
