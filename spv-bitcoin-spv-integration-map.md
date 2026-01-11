# Bitcoin SPV Integration Map

**Status**: Exploratory / Research Draft

---

## 1. Overview

This document maps how Bitcoin SPV verification integrates with Zenon's existing architectural primitives. It serves as a reference for understanding component relationships and trust boundaries.

---

## 2. Architectural Context

### 2.1 Zenon's Dual-Ledger Model

```
┌─────────────────────────────────────────────────────────────┐
│                     MOMENTUM LAYER                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │Momentum │──│Momentum │──│Momentum │──│Momentum │──►    │
│  │   N-2   │  │   N-1   │  │    N    │  │   N+1   │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
│       │            │            │            │             │
│  ─────┼────────────┼────────────┼────────────┼─────────── │
│       ▼            ▼            ▼            ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               ACCOUNT-CHAIN LAYER                    │   │
│  │  Account A: ──○──○──○──○──►                         │   │
│  │  Account B: ──○──○──○──►                             │   │
│  │  Account C: ──○──○──○──○──○──►                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Bitcoin SPV Overlay

```
┌─────────────────────────────────────────────────────────────┐
│                    BITCOIN NETWORK                          │
│  Block N-6  ──  Block N-5  ──  ...  ──  Block N  ──►       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼ Headers
┌─────────────────────────────────────────────────────────────┐
│                  HEADER RELAY LAYER (Phase 2)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Relayer  │  │ Relayer  │  │ Relayer  │   Threshold: k   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       └─────────────┼─────────────┘                        │
│                     ▼                                       │
│              Accepted Bitcoin Tip                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                VERIFICATION LAYER (Phase 0-1)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               VerifyBitcoinSPV ACI                   │   │
│  │  Input: Proof Package π                              │   │
│  │  Output: BtcFact (local) or Rejection               │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              CHECKPOINTING LAYER (Phase 3)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Optimistic Fact Checkpointing              │   │
│  │  Submit ──► PENDING ──► Challenge Window ──► FINAL   │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               INCENTIVE LAYER (Phase 4)                     │
│  ┌───────────────┐  ┌───────────────┐                      │
│  │ Bonded Relayer│  │Service Credits │                     │
│  │    Model      │  │    System      │                     │
│  └───────────────┘  └───────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Relationship to GALV

### 3.1 Genesis-Anchored Lineage Verification

GALV establishes that Zenon's genesis is anchored to Bitcoin's immutable timeline.

```
Bitcoin Genesis ──────────────────────────────────► Bitcoin Tip
        │
        │ Anchor (commitment in Bitcoin)
        ▼
Zenon Genesis ─────────────────────────────────────► Zenon Tip
```

### 3.2 SPV Extends GALV Forward

GALV provides the **initial trust anchor**.
SPV provides **ongoing verification** of Bitcoin state.

| Component | Function | Trust Source |
|-----------|----------|--------------|
| GALV | Genesis authenticity | Bitcoin anchor |
| SPV | Transaction verification | Bitcoin PoW |

### 3.3 Composition

```
Trust Chain:

1. GALV establishes: "This Zenon chain descends from authentic genesis"
2. SPV establishes: "This Bitcoin transaction is in the canonical chain"
3. Combined: "Authentic Zenon can verify canonical Bitcoin facts"
```

---

## 4. Relationship to Bounded Verification

### 4.1 Bounded Verification Primitives

The Bounded Verification Series establishes:
- **Header-Only Verification**: Validate chain without full state
- **Bounded Inclusion**: Prove state membership with limited data
- **Minimal State Frontier**: Verify with bounded resources

### 4.2 Bitcoin SPV as Bounded Verification

Bitcoin SPV is an instance of bounded verification:

| Primitive | Bitcoin SPV Equivalent |
|-----------|------------------------|
| Header-only | Bitcoin header chain |
| Bounded inclusion | Merkle proof |
| State frontier | Chain tip + confirmations |

### 4.3 Verification Guarantees

What bounded verification guarantees:
- G1: Local state consistency (tx in specific block)
- G2: Temporal coherence (confirmations at time T)
- G3: Resource bounds (O(headers) + O(log txs))

What bounded verification does NOT guarantee:
- NG1: Global validity (only verified transactions)
- NG2: Future state (may reorg)
- NG3: Cross-verifier agreement (local verification)

---

## 5. Relationship to State Proof Bundles

### 5.1 Bundle Integration

State proof bundles can embed Bitcoin SPV data:

```
StateProofBundle {
    account_block: AccountBlock
    state_delta: StateDelta
    momentum_ref: MomentumRef

    // SPV Extension
    btc_facts: BtcFact[]           // Verified facts
    btc_proof_refs: ProofRef[]     // Optional proof references
}
```

### 5.2 Cross-Chain Proof Composition

```
Light Client Verification:

1. Receive StateProofBundle
2. Verify Momentum anchor
3. Verify account-block inclusion
4. Extract BtcFact
5. Trust fact without re-verifying SPV proof
```

### 5.3 Bundle Serving

Sentries/Sentinels can serve:
- Bundles with BtcFacts
- Historical BtcFact queries
- Proof references for deep verification

---

## 6. Relationship to ACIs

### 6.1 VerifyBitcoinSPV as ACI Pattern

The `VerifyBitcoinSPV` operation follows ACI principles:

| ACI Property | Implementation |
|--------------|----------------|
| Deterministic input | Proof package π |
| Deterministic output | BtcFact or error |
| Local execution | Account verifies |
| Commitment anchoring | Fact in account state |

### 6.2 DFA Model Alignment

Bitcoin SPV exemplifies Deterministic Fact Acceptance:

```
┌─────────────────────────────────────────────────┐
│     Deterministic Fact Acceptance (DFA)         │
│                                                 │
│  Execution: Local, discardable                  │
│  Verification: Deterministic predicate          │
│  Consensus: Accepts verified facts              │
│                                                 │
│  Bitcoin SPV instance:                          │
│  - Execution: Account computes Merkle/PoW       │
│  - Verification: V(π, z) → {0,1}               │
│  - Consensus: Records BtcFact if V = 1         │
└─────────────────────────────────────────────────┘
```

### 6.3 ACI Composability

BtcFacts can trigger other ACIs:

```
Conditional ACI Execution:

1. Account A verifies BTC payment → BtcFact
2. Account A invokes ReleaseEscrow ACI
3. ReleaseEscrow checks: HasBtcFact(A, payment_tx, 6)?
4. If true: Release funds
5. If false: Reject
```

---

## 7. Verification Stack Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Cross-chain │  │   Bridges   │  │  Oracles    │         │
│  │  Payments    │  │             │  │             │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CHECKPOINT LAYER                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          Global BtcCheckpoints (Phase 3)             │    │
│  │     PENDING → CHALLENGED → FINALIZED/INVALIDATED     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                     FACT LAYER                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Local BtcFacts (Phase 1)                   │    │
│  │         Per-account verified facts                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                  VERIFICATION LAYER                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        VerifyBitcoinSPV ACI (Phase 0)                │    │
│  │   PoW + Chainwork + Merkle + Depth checks            │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Header Relay Protocol (Phase 2)              │    │
│  │      Bitcoin headers from threshold sources          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   BITCOIN NETWORK                            │
│             (External, not Zenon-controlled)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Trust Boundaries

### 8.1 Trust Boundary Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  ZENON TRUST DOMAIN                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VERIFIED FACTS                                      │   │
│  │  - BtcFacts in account state                        │   │
│  │  - Finalized BtcCheckpoints                         │   │
│  │  - Trust: Cryptographic verification                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PENDING FACTS                                       │   │
│  │  - Unfinalized checkpoints                          │   │
│  │  - Trust: Optimistic + economic                     │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Trust Boundary
                             │
┌────────────────────────────▼────────────────────────────────┐
│  EXTERNAL TRUST DOMAIN                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  BITCOIN CHAIN                                       │   │
│  │  - Trust: Bitcoin consensus (honest majority)       │   │
│  │  - Assumption: q < 0.5 hashpower adversarial        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  HEADER SOURCES                                      │   │
│  │  - Trust: Threshold relay (k independent sources)   │   │
│  │  - Assumption: < k sources colluding                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Trust Assumptions by Layer

| Layer | Trust Assumption |
|-------|------------------|
| Bitcoin PoW | Honest majority (q < 0.5) |
| Header relay | k independent sources |
| SPV verification | Correct implementation |
| Local facts | Verifying account |
| Checkpoints | Economic (bond + fraud proofs) |
| Applications | Application-specific |

### 8.3 Trust Minimization

Each layer minimizes trust:

| Traditional Bridge | Bitcoin SPV on Zenon |
|--------------------|----------------------|
| Trust n-of-m signers | Trust Bitcoin PoW |
| Single key compromise breaks | Requires majority hashpower |
| Operator liveness required | Permissionless verification |
| Centralized custody | No custody |

---

## 9. Data Flow

### 9.1 Verification Flow

```
User wants to verify BTC payment:

1. Obtain proof package π from:
   - Personal Bitcoin node
   - Block explorer API
   - Header relay service

2. Submit to VerifyBitcoinSPV ACI:
   → Headers validated (PoW, linkage)
   → Merkle proof validated
   → Depth confirmed

3. BtcFact stored in account state

4. (Optional) Submit for global checkpoint:
   → Bond posted
   → Challenge window
   → Finalization
```

### 9.2 Query Flow

```
User wants to check if payment verified:

1. Query local facts:
   GetBtcFact(account, tx_hash)

2. Or query global checkpoints:
   GetBtcCheckpoint(tx_hash)

3. Verify finalization status:
   - PENDING: Not yet final
   - FINALIZED: Globally accepted
   - INVALIDATED: Proven false
```

---

## 10. Summary

Bitcoin SPV on Zenon integrates cleanly with existing architecture:

| Zenon Component | SPV Integration |
|-----------------|-----------------|
| GALV | SPV extends genesis anchoring forward |
| Bounded Verification | SPV is an instance of bounded verification |
| State Proof Bundles | BtcFacts embeddable in bundles |
| ACIs | VerifyBitcoinSPV follows ACI pattern |
| DFA Model | SPV exemplifies deterministic fact acceptance |

The integration respects Zenon's core principles:
- **Local verification, global commitment**
- **Determinism before economics**
- **Optionality before consensus coupling**

---

## 11. References

- [GALV Specification](/docs/specs/GALV_spec_draft.md)
- [GALV Composition](/docs/architecture/galv-composition-with-bounded-verification.md)
- [Bounded Verification Series](/docs/research/bounded-verification-series.md)
- [State Proof Bundles](/docs/notes/state-proof-bundles.md)
- [Taxonomy: Deterministic Fact Acceptance](/docs/research/taxonomy-deterministic-fact-acceptance.md)
- [Engineering Roadmap — Bitcoin SPV](/docs/research/engineering-roadmap-bitcoin-spv.md)
