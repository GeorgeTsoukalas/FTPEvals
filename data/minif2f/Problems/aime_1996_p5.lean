import Mathlib

theorem aime_1996_p5
  (a b c r s t : ℂ)
  (hroots : {a, b, c} = (Cubic.mk 1 3 4 (-11)).roots)
  (hroots' : {a + b, b + c, c + a} = (Cubic.mk 1 r s t).roots) :
  t = 23 := by
  sorry
