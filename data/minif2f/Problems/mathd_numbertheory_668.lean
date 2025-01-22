import Mathlib

theorem mathd_numbertheory_668
  (L R a b : ZMod 7)
  (ha : a = 2)
  (hb : b = 3)
  (hL : L = (a + b )⁻¹)
  (hR : R = a⁻¹ + b⁻¹) :
  L.val - R.val = 1 := by
  sorry
