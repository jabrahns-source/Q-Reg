// Q-REG Runtime (Rust)
// Formal proofs live in ../formal/*.idr (Idris 2 dependent types).
// This binary is the thin deterministic runtime host.
// gRPC surface and full Idris extraction bridge remain under construction.
// Current surface mirrors the pure decision procedures of qreg_engine.py
// for cross-language determinism verification.

use std::collections::BTreeMap;

const SCOPE1_YELLOW: f64 = 50_000.0;
const SCOPE1_BLACK: f64 = 250_000.0;
const RTM_YELLOW: f64 = 0.35;
const RTM_BLACK: f64 = 0.50;

#[derive(Debug, Clone, PartialEq, Eq)]
enum GateState {
    Green,
    Yellow,
    Black,
}

impl GateState {
    fn as_str(&self) -> &'static str {
        match self {
            GateState::Green => "GREEN",
            GateState::Yellow => "YELLOW",
            GateState::Black => "BLACK",
        }
    }
}

#[derive(Debug)]
struct GateResult {
    state: GateState,
    citations: Vec<&'static str>,
    reasons: Vec<String>,
}

fn classify_gate(scope1_mte: f64, rtm_factor: f64) -> GateResult {
    let mut citations = Vec::new();
    let mut reasons = Vec::new();

    let state = if scope1_mte >= SCOPE1_BLACK || rtm_factor >= RTM_BLACK {
        citations.push("Title 17 CCR §95111(f)");
        if scope1_mte >= SCOPE1_BLACK {
            reasons.push(format!("scope1_mte={} >= {}", scope1_mte, SCOPE1_BLACK));
        }
        if rtm_factor >= RTM_BLACK {
            reasons.push(format!("rtm_factor={} >= {}", rtm_factor, RTM_BLACK));
        }
        GateState::Black
    } else if scope1_mte >= SCOPE1_YELLOW || rtm_factor >= RTM_YELLOW {
        citations.push("Title 17 CCR §95111(c)");
        if scope1_mte >= SCOPE1_YELLOW {
            reasons.push(format!("scope1_mte={} >= {}", scope1_mte, SCOPE1_YELLOW));
        }
        if rtm_factor >= RTM_YELLOW {
            reasons.push(format!("rtm_factor={} >= {}", rtm_factor, RTM_YELLOW));
        }
        GateState::Yellow
    } else {
        citations.push("Title 17 CCR §95111(a)");
        reasons.push("within GREEN thresholds".to_string());
        GateState::Green
    };

    GateResult {
        state,
        citations,
        reasons,
    }
}

fn main() {
    println!("Q-REG Runtime v0.1.1 (deterministic gate surface)");
    println!("Formal proofs: Compliance, GateLogic, LinearLifecycle, Provenance, Moat (Idris 2)");
    println!("Reference engine: ../qreg_engine.py remains the full sealing + Merkle surface");
    println!("Status: pure classification mirrored; gRPC + proof extraction bridge pending");
    println!();

    // Deterministic demo vectors matching Python test cases
    let samples: Vec<(&str, f64, f64)> = vec![
        ("FAC-GREEN-01", 12_000.0, 0.22),
        ("FAC-YELLOW-02", 78_000.0, 0.41),
        ("CALPORTLAND-REDDING", 372_761.0, 0.428),
    ];

    for (entity, scope1, rtm) in samples {
        let result = classify_gate(scope1, rtm);
        println!(
            "{}: gate={} citations={:?}",
            entity,
            result.state.as_str(),
            result.citations
        );
        for r in &result.reasons {
            println!("  reason: {}", r);
        }
    }

    println!();
    println!("All decisions are pure functions of inputs + fixed policy constants.");
    println!("No randomness. No external calls. Cross-language parity with Python engine.");
}
