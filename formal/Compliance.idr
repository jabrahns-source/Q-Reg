module Compliance

import Data.Nat

-- Generic Regulation (the key agnostic abstraction)
record Regulation where
  constructor MkRegulation
  name        : String
  deadlineDays : Nat

-- Pre-defined example regulations (California as first-class examples)
ccpa : Regulation
ccpa = MkRegulation "CCPA" 45

dfpi : Regulation
dfpi = MkRegulation "DFPI" 30

sb253 : Regulation
sb253 = MkRegulation "SB253" 60

-- Days wrapper stays the same
data Days : Nat -> Type where
  MkDays : (d : Nat) -> Days d

-- Core state machine (unchanged)
data RequestState : Type where
  Received : RequestState
  Verified : RequestState
  Processed : RequestState
  Fulfilled : RequestState
  Expired : RequestState

data LinearRequest : RequestState -> Type where
  MkReq : (id : String) -> (state : RequestState) -> LinearRequest state

processRequest : (1 req : LinearRequest Received) -> LinearRequest Verified
processRequest (MkReq id Received) = MkReq id Verified

verifyIdentity : (1 req : LinearRequest Verified) -> LinearRequest Processed
verifyIdentity (MkReq id Verified) = MkReq id Processed

-- Now generic over any Regulation
fulfillDeletion : (reg : Regulation) ->
                 (1 req : LinearRequest Processed) ->
                 (d : Days days) ->
                 {auto prf : LTE days (deadlineDays reg)} ->
                 LinearRequest Fulfilled
fulfillDeletion _ (MkReq id Processed) (MkDays d) = MkReq id Fulfilled

-- Generic impossibility theorem (works for any regulation)
impossibleViolation : (reg : Regulation) ->
                     (days : Nat) ->
                     (prfGT : GT days (deadlineDays reg)) ->
                     (prfLTE : LTE days (deadlineDays reg)) ->
                     Void
impossibleViolation _ days prfGT prfLTE =
  absurd (gtImpliesNotLte prfGT prfLTE)
  where
    gtImpliesNotLte : GT m n -> LTE m n -> Void
    gtImpliesNotLte (LTESucc x) LTEZero impossible = impossible
    gtImpliesNotLte (LTESucc x) (LTESucc y) prf = gtImpliesNotLte x y prf

-- Convenience functions for California (backward compatible style)
fulfillCCPADeletion : (1 req : LinearRequest Processed) -> (d : Days days) -> {auto prf : LTE days 45} -> LinearRequest Fulfilled
fulfillCCPADeletion = fulfillDeletion ccpa

impossibleCCPAViolation : (days : Nat) -> (prfGT : GT days 45) -> (prfLTE : LTE days 45) -> Void
impossibleCCPAViolation = impossibleViolation ccpa