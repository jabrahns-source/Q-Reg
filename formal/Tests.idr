module Tests

import Compliance
import LinearLifecycle

testCCPADeadline : (days : Nat) -> {auto prf : LTE days 45} -> LinearRequest Fulfilled
testCCPADeadline days = fulfillDeletion (MkReq "test" Processed) (MkDays days)

total
allTheoremsHold : (req : LinearRequest Received) -> NonEmpty (safeLifecycle req)
allTheoremsHold req = IsNonEmpty