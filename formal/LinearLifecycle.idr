module LinearLifecycle

import Compliance
import Data.Nat

data ComplianceAction : (from : RequestState) -> (to : RequestState) -> Type where
  Verify : ComplianceAction Received Verified
  Process : ComplianceAction Verified Processed
  Fulfill : (d : Days days) -> {auto prf : LTE days 45} -> ComplianceAction Processed Fulfilled
  Expire : ComplianceAction Processed Expired

transition : (1 req : LinearRequest from) -> (act : ComplianceAction from to) -> LinearRequest to
transition req Verify = processRequest req
transition req Process = verifyIdentity req
transition req (Fulfill d {prf}) = fulfillDeletion req d
transition req Expire = MkReq "expired" Expired

total
safeLifecycle : (1 req : LinearRequest Received) -> LinearRequest Fulfilled
safeLifecycle req = 
  let v = transition req Verify
      p = transition v Process
  in transition p (Fulfill (MkDays 30))

total
noLateFulfill : (days : Nat) -> (prfGT : GT days 45) -> LinearRequest Processed -> Void
noLateFulfill days prfGT req = 
  let impossiblePrf : LTE days 45 = absurd (gtNotLte prfGT)
  in impossibleViolation days prfGT impossiblePrf
  where
    gtNotLte : GT m n -> LTE m n -> Void
    gtNotLte (LTESucc x) LTEZero = absurd x
    gtNotLte (LTESucc x) (LTESucc y) = gtNotLte x y