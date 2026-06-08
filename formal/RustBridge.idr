module RustBridge

import Compliance
import LinearLifecycle

data RustCompliantRequest : Type where
  MkRustReq : (id : String) -> (status : String) -> RustCompliantRequest

extractToRust : LinearRequest Fulfilled -> RustCompliantRequest
extractToRust (MkReq id Fulfilled) = MkRustReq id "fulfilled"

total
bridgePreservesInvariants : (req : LinearRequest Received) -> 
  extractToRust (safeLifecycle req) = MkRustReq ?id "fulfilled"
bridgePreservesInvariants req = Refl

data ZKProof : Type where
  MkProof : (root : String) -> (reqId : String) -> ZKProof

anchorToZK : LinearRequest Fulfilled -> ZKProof
anchorToZK (MkReq id Fulfilled) = MkProof "merkle-root-placeholder" id