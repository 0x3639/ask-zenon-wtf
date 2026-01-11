# Execution Model

How application logic runs in Zenon without a global VM.

---

## Overview

Zenon's execution model is local first. Instead of running smart contracts on a global virtual machine, users execute deterministic programs locally and commit only the results to their account-chains. Consensus nodes validate commitments, they never re-execute application logic.

This enables:

- Browser native execution via WASM or JavaScript
- Parallel, non-competing workloads
- Extremely cheap interactions without fee markets
- Scalability without global state bottlenecks

---

## Key Concepts

**zApps** — Deterministic programs executed by the user, with results anchored to the account-chain. Consensus only verifies that commitments are valid and transitions are well formed.

**Local First Design** — Each user has their own account-chain, local state, and execution environment. No global VM interprets or runs application code.

**Dynamic Plasma** — Adaptive resource constraints that regulate state growth and throughput without introducing fees. Plasma difficulty adjusts based on system load rather than competitive bidding.

---

## Documents in This Section

- [zApps Draft Notes](zapps-draft-notes.md) — How application logic runs locally, remains deterministic, and anchors verifiable results to the dual-ledger. Covers the minimal workflow from local execution to Momentum finalization.

- [zApps Draft Notes (Extended)](zapps-draft-notes/README.md) — Extended drafts and deeper exploration of the zApp execution model.

- [Dynamic Plasma](dynamic-plasma.md) — Adaptive mechanism for regulating resource consumption. Explains how plasma difficulty adjusts to state growth while preserving a feeless user experience.
