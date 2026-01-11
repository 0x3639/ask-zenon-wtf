# Light Clients & Verification

Research into trustless verification models for resource-constrained environments.

---

## Overview

Zenon's dual-ledger architecture enables lightweight verification without global state. Light clients can verify chain progress and account-chain updates using only:

- Momentum headers
- Compact state proofs
- Local account-chain data

This aligns naturally with SPV-style verification, making browser native and mobile clients viable as first class network participants.

---

## Key Concepts

**Header-Only Verification** — Light nodes verify chain progress by validating Momentum headers (Pillar signatures, difficulty, weight) without downloading full blocks or global state.

**State Proof Bundles** — Compact verification primitives that prove account-chain transitions without Merkle proofs or global state access.

**Browser as Peer** — Modern browsers can perform cryptographic verification using WASM and P2P transports, enabling trustless participation without RPC gateways.

---

## Documents in This Section

- [Momentum Header Verification](momentum-header-verification.md) — How light nodes verify chain progress: Pillar eligibility, chain continuity, and account-chain finality using only headers.

- [SPV Light Verification](spv-light-verification.md) — Exploration of SPV-style verification for Zenon. Covers header verification, proof acceptance, and minimal state maintenance.

- [SPV Light Verification (Extended)](spv-light-verification/README.md) — Extended notes on SPV patterns and implementation considerations.

- [State Proof Bundles](state-proof-bundles.md) — Compact verification primitive for account-chain transitions. Explains why Merkle proofs aren't needed in the dual-ledger model.

- [Browser Light Client](browser-light-client.md) — Early notes on minimal browser client: header sync, local signing, micro PoW generation, and transaction relay.

- [Browser Light Client Architecture](browser-light-client-architecture.md) — Comprehensive research on browsers as verifiable peers. Covers verification responsibilities, networking, and state reconstruction.

- [Browser Light Client (Extended)](browser-light-client/README.md) — Extended drafts and deeper exploration of browser client design.
