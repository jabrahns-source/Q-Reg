// Q-REG Runtime (Rust)
// Formal proofs live in ../formal/*.idr (Idris 2 dependent types).
// This binary is the thin runtime host that will eventually load
// extracted proofs / decision procedures and expose a deterministic
// gRPC surface matching the Python reference engine.

fn main() {
    println!("Q-REG Runtime v0.1");
    println!("Formal proofs: Compliance, GateLogic, LinearLifecycle, Provenance, Moat");
    println!("Status: proofs present; runtime bridge and gRPC surface under construction");
    println!("Reference engine: ../qreg_engine.py (Python) is the current executable surface");
}
