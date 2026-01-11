# Node Architecture

Overview of Zenon's node hierarchy and their roles in the Network of Momentum.

---

## The Node Hierarchy

Zenon separates consensus from execution across a layered node architecture:

```
Sentries (Local Execution & Light Client Support)
    ↓
Supervisors (Aggregation & Proof Construction)
    ↓
Sentinels (Verification & Filtering)
    ↓
Pillars (Consensus)
```

Each layer has distinct responsibilities:

1. **Sentries** — Execution layer. Run zApps locally, serve proofs to light clients.
2. **Supervisors** — Coordination layer. Aggregate Sentry outputs, construct State Proof Bundles.
3. **Sentinels** — Verification layer. Validate structure and filter spam before data reaches consensus.
4. **Pillars** — Consensus layer. Produce Momentums, finalize ordering, apply deterministic state deltas.

---

## Key Insight

> "Zenon consensus finalizes commitments to facts, not the correctness of execution that produced them."

Execution happens at the edge (Sentries), not at consensus (Pillars). Pillars commit results, not processes. This separation enables scalability without sacrificing verification guarantees.

---

## Documents in This Section

- [Pillars](pillars.md) — Consensus nodes that produce Momentums. They validate ordering and state transitions but don't execute contract logic.

- [Sentinel Finalization Layer](sentinel-finalization-layer.md) — Explores Sentinels as a verification bridge between account-chains and Pillars, reducing the validation burden on consensus.

- [Sentinel Middle Layer](sentinel-middle-layer.md) — Frames Sentinels as the deterministic verification and relay layer. Covers what they verify: structure, PoW, contract calls, transactions.

- [Supervisor Layer](supervisor-layer.md) — Proposes an intermediate coordination layer that aggregates Sentry outputs, validates proof completeness, and constructs State Proof Bundles.

- [Minimal Sentry Node](minimal-sentry-node.md) — Describes the smallest useful Sentry: no global state, modest hardware requirements, serves as a bridge between light clients and the network.

- [Minimal Sentry Node (Extended)](minimal-sentry-node/README.md) — Extended notes and deeper exploration of Sentry design.