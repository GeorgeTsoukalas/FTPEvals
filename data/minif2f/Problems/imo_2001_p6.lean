import Mathlib

theorem imo_2001_p6
  (K L M N : ℤ)
  (h₀ : 0 < N)
  (h₁ : N < M)
  (h₂ : M < L)
  (h₃ : L < K)
  (h₄ : K * M + L * N = (K + L - M + N) * (-K + L + M + N)) :
  ¬ Nat.Prime (K * L + M * N).natAbs := by
  sorry
