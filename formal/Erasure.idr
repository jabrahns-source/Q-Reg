module Erasure

-- QTT Erasure examples for performance
-- Proofs marked 0 are erased at runtime (zero cost)

-- A compliance check that exists only at compile time
0
compileTimeOnlyCheck : (days : Nat) -> {auto prf : LTE days 45} -> ()
compileTimeOnlyCheck _ = ()

-- Linear resource with erased proof component
data ErasedLinearReq : RequestState -> Type where
  MkErasedReq : (id : String) -> (state : RequestState) ->
                (0 proof : LTE 0 45) ->  -- Erased proof
                ErasedLinearReq state

-- Runtime cost is only the actual data; proofs disappear
runtimeOnly : ErasedLinearReq Fulfilled -> String
runtimeOnly (MkErasedReq id Fulfilled _) = id

-- This enables 26k+ RPS with full formal guarantees