module Deadlines

import Compliance
import Data.Nat

-- Dependent type for time-bounded actions
-- A fulfillment proof indexed by actual days taken
record FulfillmentProof (days : Nat) where
  constructor MkFulfillment
  reqId : String
  actualDays : Days days
  {auto prf : LTE days 45}  -- Enforced at construction

-- Theorem: Any fulfillment within window is valid
validWithinWindow : (days : Nat) -> (prf : LTE days 45) -> FulfillmentProof days -> Type
validWithinWindow days prf proof = LTE days 45

-- Impossible late fulfillment (extended with dependent index)
impossibleLateFulfillment : (days : Nat) -> (prfGT : GT days 45) -> FulfillmentProof days -> Void
impossibleLateFulfillment days prfGT (MkFulfillment _ (MkDays d) {prf}) = 
  impossibleViolation days prfGT prf

-- Linear resource with time index for advanced workflows
data TimedLinearRequest : RequestState -> Nat -> Type where
  MkTimedReq : (id : String) -> (state : RequestState) -> (timestamp : Nat) -> TimedLinearRequest state timestamp

-- Transition that tracks elapsed time (dependent)
fulfillTimed : (1 req : TimedLinearRequest Processed elapsed) -> 
             (d : Days days) -> 
             {auto prf : LTE (elapsed + days) 45} ->  -- Cumulative time check
             TimedLinearRequest Fulfilled (elapsed + days)
fulfillTimed (MkTimedReq id Processed elapsed) (MkDays d) = 
  MkTimedReq id Fulfilled (elapsed + d)