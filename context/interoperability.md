# Interoperability

Cross-chain verification concepts and external data integration.

---

## Overview

Zenon can consume external chain data as a unilateral fact oracle, verifying external consensus outputs (finality, ordering, cost) without executing external protocols or coordinating bidirectionally. This enables trustless cross-chain verification using standard cryptographic primitives.

The dual-ledger architecture is structurally compatible with:

- Bitcoin SPV header verification
- Merkle inclusion proofs for external transactions
- Bounded verification patterns like HTLCs and PTLCs

---

## Key Concepts

**Unilateral Verification** — Zenon verifies external facts without participating in external consensus. External data becomes a committed fact once verified, requiring no ongoing coordination.

**Bitcoin SPV Compatibility** — Bitcoin transaction verification is cryptographically possible using only header PoW verification, cumulative chainwork, Merkle proofs, and confirmation depth.

**Bounded Verification Primitives** — HTLCs and PTLCs are special cases of bounded inclusion accepting state transitions when small, verifiable conditions are satisfied without re-executing global state.

---

## Documents in This Section

- [Bitcoin SPV Feasibility](bitcoin-spv-feasibility.md) — Why Bitcoin transaction verification via SPV is cryptographically possible within Zenon's ledger model. Covers PoW headers, chainwork, Merkle proofs, and confirmation security.

- [HTLCs, PTLCs, and Bounded Inclusion](htlc_ptlc_and_bounded_inclusion_comparison.md) — How familiar primitives like HTLCs and PTLCs relate to bounded inclusion. Clarifies that bounded verification is a generalization of patterns already proven successful.
