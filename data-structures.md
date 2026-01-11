# Data Structures & Commitments

How data is organized and committed in Zenon's dual-ledger architecture.

---

## Overview

Zenon's dual-ledger model commits to state transitions rather than transactions. The account-chain DAG handles user activity while Momentums finalize references to those chains. This separation enables lightweight verification without requiring Merkle inclusion proofs or global state replay.

---

## Key Concepts

**ChangesHash** — A cryptographic digest representing the aggregate effect of all account-chain transitions included in a Momentum. It commits to balance updates, confirmation heights, and all deterministic state machine components.

**Account-Chain Frontiers** — Each account-chain is internally ordered and self verifying. A new account-block implicitly validates all previous blocks, making frontier verification sufficient for proving inclusion.

**Momentum Data Field** — A reserved header field that is hash-committed but currently unused. This provides an extension point for future protocol features like cross-chain commitments or succinct proof anchoring.

---

## Documents in This Section

- [Account Chain Commitments](account-chain-commitments.md) — How account-chain transitions are committed inside Momentums. Explains ChangesHash, why Merkle proofs aren't required, and the frontier verification model.

- [Momentum Data Fields](momentum-data-fields.md) — Analysis of the Momentum Data field as a protocol extension point. Covers potential uses for cross-chain commitments, proof anchoring, and parameter signaling.
