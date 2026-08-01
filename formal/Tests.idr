module Tests

import Compliance
import LinearLifecycle
import GateLogic
import Provenance
import Moat
import Deadlines
import Erasure

%default total

-- CCPA / Delete Act deadline preservation under linear lifecycle
testCCPADeadline : (days : Nat) -> {auto prf : LTE days 45} -> LinearRequest Fulfilled
testCCPADeadline days = fulfillDeletion (MkReq "test" Processed) (MkDays days)

-- All safe lifecycles are non-empty (totality + productivity)
allTheoremsHold : (req : LinearRequest Received) -> NonEmpty (safeLifecycle req)
allTheoremsHold req = IsNonEmpty

-- Gate logic: violation states are unrepresentable once proven
gateRejectsViolation : (g : Gate) -> (s : State) -> {auto prf : IsViolation s} -> Not (Accepts g s)
gateRejectsViolation g s prf = gateUnacceptability g s prf

-- Provenance chain remains intact under erasure of personal data
provenanceSurvivesErasure : (p : Provenance) -> (e : Erasure) -> Intact (applyErasure p e)
provenanceSurvivesErasure p e = erasurePreservesChain p e

-- Moat: external observation cannot forge a valid sealed receipt
moatNoForge : (r : Receipt) -> (ext : External) -> Not (Forgeable r ext)
moatNoForge r ext = moatProperty r ext

-- Deadlines: overdue requests transition only through linear states
deadlineLinear : (d : Deadline) -> Linear (transition d)
deadlineLinear d = deadlineIsLinear d
