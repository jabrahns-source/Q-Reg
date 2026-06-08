module Compliance

import Data.Nat

data Days : Nat -> Type where
  MkDays : (d : Nat) -> Days d

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

fulfillDeletion : (1 req : LinearRequest Processed) -> (d : Days days) -> {auto prf : LTE days 45} -> LinearRequest Fulfilled
fulfillDeletion (MkReq id Processed) (MkDays d) = MkReq id Fulfilled

impossibleViolation : (days : Nat) -> (prfGT : GT days 45) -> (prfLTE : LTE days 45) -> Void
impossibleViolation days prfGT prfLTE = absurd (gtImpliesNotLte prfGT prfLTE)
  where
    gtImpliesNotLte : GT m n -> LTE m n -> Void
    gtImpliesNotLte (LTESucc x) LTEZero impossible = impossible
    gtImpliesNotLte (LTESucc x) (LTESucc y) prf = gtImpliesNotLte x y prf