import Lake
open Lake DSL

package «minif2f» where
  -- add package configuration options here

lean_lib «Minif2f» where
  -- add library configuration options here

@[default_target]
lean_exe «minif2f» where
  root := `Main

require mathlib from git "https://github.com/leanprover-community/mathlib4" @ "v4.15.0"
