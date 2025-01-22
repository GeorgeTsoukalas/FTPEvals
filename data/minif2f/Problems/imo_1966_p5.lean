import Mathlib

theorem imo_1966_p5
 (x a : Fin 4 → ℝ)
 (ha : StrictAnti a)
 (h1 : abs (a 0 - a 1) * x 1 + abs (a 0 - a 2) * x 2 + abs (a 0 - a 3) * x 3 = 1)
 (h2 : abs (a 1 - a 0) * x 0 + abs (a 1 - a 2) * x 2 + abs (a 1 - a 3) * x 3 = 1)
 (h3 : abs (a 2 - a 0) * x 0 + abs (a 2 - a 1) * x 1 + abs (a 2 - a 3) * x 3 = 1)
 (h4 : abs (a 3 - a 0) * x 0 + abs (a 3 - a 1) * x 1 + abs (a 3 - a 2) * x 2 = 1) :
 x 1 = 0 ∧ x 2 = 0 ∧ x 0 = 1 / abs (a 0 - a 3) ∧ x 3 = 1 / abs (a 0 - a 3) := by sorry
