# zApps

Proof-First Verifiable Applications under Bounded Verification

# Abstract

This paper specifies zApps, a proof-first application model for distributed systems where verification—not execution—is architecturally primary. zApps are verifiable application state machines whose correctness is established by cryptographic proofs rather than global execution replay.

Unlike execution-first platforms, zApps do not assume synchronous execution, global state visibility, or unbounded verifier resources. They operate within bounded verification environments where clients—browsers or light nodes—reason about application correctness under finite memory, bandwidth, and partial data availability constraints.

zApps are not a virtual machine, not a rollup, and not a general-purpose execution layer. They are an application paradigm for systems that prioritize verifier sovereignty, operating in alignment with genesis-anchored lineage verification, refusal-forward semantics, and edge-native participation.

# 1. Motivation: Why Execution-First Platforms Fail at the Edge

Blockchain application platforms assume execution correctness implies verification correctness. This assumption requires:

- Verifiers can replay all execution

- Full transaction history remains available

- State growth is bounded and persistable

- Verifier resources match producer resources

These requirements fail in resource-constrained environments: browsers, mobile devices, offline nodes, hostile networks. As systems scale, the cost of verifying execution asymptotically approaches the cost of executing it—eliminating the verification advantage entirely.

Light clients are therefore forced to trust intermediaries: RPC endpoints, indexers, sequencers, rollup operators. This recreates the trust asymmetries that motivated distributed verification.

zApps invert this architecture. The foundational premise:

If a verifier cannot independently verify an application's effects, the application does not exist for that verifier.

This is not a usability constraint. It is an architectural commitment to verifier sovereignty.

# 2. Formal Definition

A zApp is a verifiable application state machine where correctness is established by proofs rather than execution traces. The prefix “z” denotes zero reliance on execution replay, distinguishing this model from zero-knowledge-specific constructions.

Definition 2.1. A zApp is a tuple  $\mathcal{A} = (S, T, C, \Pi)$  where:

-  $S$  is the application state space

-  $T: S \times I \to S$  is a deterministic state transition function, where  $I$  is the input space

-  $C: S \to \{0,1\}^*$  is a commitment scheme mapping states to fixed-length digests

-  $\Pi \subseteq S \times I \times S \times \{0,1\}^*$  is a proof relation where  $(s,i,s',\pi) \in \Pi$  attests that  $T(s,i) = s'$ .

Execution of  $T$  occurs off-chain by application producers. Verification of  $\Pi$  occurs on-chain by processors and clients. The chain never replays  $T$ .

Validator and clients verify:

1.  $(s_{i - 1},i_i,s_i,\pi_i)\in \Pi$  for each claimed transition

2.  $C(s_{i})$  is consistent with prior commitment  $c_{i - 1} = C(s_{i - 1})$

3. Proof  $\pi_i$  satisfies bounded verification constraints (size, computation)

This inverts the verification burden. Traditional platforms verify by re-executing  $T$ . zApps verify by checking  $\Pi$  — a fundamentally different architectural constraint.

# 2.1 Minimal Illustrative Example

Consider an abstract token ledger where  $S = \{ \text{accounts} \to \text{balances} \}$ . A transfer defines  $T$ : given  $s = \{ A : 100, B : 50 \}$  and input  $i =$  "transfer 30 from A to B", the function produces  $s' = \{ A : 70, B : 80 \}$ .

The commitment  $C(s')$  is a Merkle root or cryptographic hash of the resulting state. The proof  $\pi$  attests: (1)  $s[A] \geq 30$ , (2)  $s'[A] = s[A] - 30$  and  $s'[B] = s[B] + 30$ , (3) all other accounts remain unchanged.

A verifier receives commitment  $c_{i-1}$ , commitment  $c_i$ , and proof  $\pi_i$ . It verifies  $(s_{i-1}, i, s_i, \pi_i) \in \Pi$  without replaying the transfer logic, without storing full state  $S$ , and without trusting the producer's execution.

If verification exceeds resource bounds, the verifier refuses—an architecturally correct outcome, not a failure. This example is intentionally abstract; no virtual machine, protocol, or cryptographic construction is assumed.

# 3. The Proof-First Inversion

Traditional smart contract platforms assume correctness emerges from universal execution:

"If all processors execute the same code, correctness follows."

This model couples verification cost to execution complexity. As applications grow more complex, verification becomes more expensive—eventually matching the cost of execution itself.

zApps invert this relationship:

"If correctness is proven, execution is irrelevant to verification."

This inversion has architectural consequences:

- Validators need not understand application logic—they verify proofs, not semantics

- Clients need not trust execution environments—proofs are self-authenticating

- Application complexity does not increase verifier cost—proof bounds remain constant

Proofs encode semantic correctness (what changed) rather than procedural steps (how it changed). This decouples application evolution from verification infrastructure.

# 4. Bounded Verification as Architectural Foundation

zApps are designed explicitly for resource-bounded verifiers. Verification bounds are not implementation details—they are first-class architectural constraints.

Definition 4.1. A verification operation is bounded if:

Proof size is  $O(\log N)$  where  $N$  is the number of application state elements

Verification computation is  $O(\log N)$  or  $O(1)$  in cryptographic operations

- Retained state is  $O(k)$  where  $k$  is the number of actively verified applications

- Historical scope is finite and explicitly declared

A verifier operating under these bounds maintains: a recent commitment frontier, a minimal set of application-specific proofs, and local coherence guarantees within its scope.

When a verification request exceeds these bounds—whether in proof size, computation cost, or historical depth—the verifier refuses. This refusal is not a failure mode. It is the correct response to a query outside the verifier's security boundary.

Refusal semantics preserve honesty under constraint. A verifier that claims to verify unbounded history is either dishonest (relying on unverified assumptions) or resource-unbounded (matching producer capacity). Bounded verifiers acknowledge their limits explicitly.

# 5. Commitment Chains and Genesis-Anchored Composition

Each zApp maintains a commitment chain linking state transitions:

$$
c _ {i} = H (c _ {i - 1} \parallel \Delta_ {i})
$$

where  $\Delta_{i}$  represents an application state update at height  $i$ ,  $H$  is a collision-resistant hash function, and  $\parallel$  denotes concatenation.

The underlying blockchain orders these commitments but does not interpret them. The chain provides a single global guarantee: commitments are sequentially ordered, immutable once finalized, and verifiable via lineage proofs.

zApps compose with external commitment backbones—such as genesis-anchored lineage verification systems—without depending on their specific implementation. The composition requires only that commitment ordering is verifiable and that proofs remain bounded.

This design separates application logic (the semantics of  $\Delta_{i}$ ) from ordering logic (the sequencing of  $c_{i}$ ). Verifiers need not understand the former to verify the latter.

# 6. Verification Without Execution Replay

A core principle: verifiers never replay application execution.

Instead, verification operates on three primitives:

1. Proof validity: Does  $\pi_i$  correctly attest that transition  $\Delta_i$  is valid?

2. Commitment linkage: Does  $c_{i}$  correctly reference  $c_{i-1}$ ?

3. State coherence: Are retained proofs consistent with the current frontier?

These operations are bounded by construction. Proof validity checks are  $O(\log N)$  or  $O(1)$ . Commitment linkage is  $O(1)$  hash verification. State coherence checks scale with the verifier's retention policy, not global state size.

Contrast this with execution-first verification: to verify a state transition, the verifier must replay the execution of  $T$ . As  $T$  grows more complex, verification cost grows proportionally. At scale, verification becomes indistinguishable from execution.

zApps eliminate this coupling. Verification cost scales with proof complexity, not application complexity. This is the architectural advantage of proof-first systems.

# 7. Composition Without Global Atomicity

zApps do not compose via synchronous function calls. Global atomicity—where all applications observe identical state simultaneously—is incompatible with bounded verification.

Instead, composition occurs through:

- Shared commitment references: Application A includes  $c_{B,j}$  in its state

Cross-application proofs: Proof  $\pi_{A,i}$  attests to consistency with  $c_{B,j}$

- Snapshot-consistent verification: Verifiers check proofs against declared commitment heights

This model trades atomic composability (all applications see the same state at the same logical time) for verifier independence (each verifier maintains its own frontier and refuses operations outside its scope).

The trade-off is necessary. Atomic composability requires:

- Global state visibility (unbounded storage)

- Synchronous execution (unbounded computation)

- Universal agreement on current state (unbounded coordination)

These requirements violate bounded verification constraints. zApps therefore accept eventual consistency across applications while preserving local consistency within each verifier's scope.

Composition is verified, not executed. This preserves verifier sovereignty at the cost of global synchrony.

# 8. Client Perspective: Edge-Native Verification

From a browser or light client perspective, zApps provide distinct verification guarantees:

- Independent verification of application effects without trusting intermediaries

- Explicit refusal when proofs exceed verification bounds

- Clear declaration of verification scope (frontier height, retention horizon)

- No reliance on RPC trust assumptions or full node access

This aligns zApps with refusal-forward user experience design, where the system explicitly communicates what it can and cannot verify. Traditional light clients either trust RPC providers or silently degrade to insecure modes. zApps refuse insecure operations explicitly.

Consider a browser-based verifier tracking a payment application:

The client maintains commitments  $c_{1000}$  through  $c_{1100}$ . When queried about state at height 900 (outside its frontier), it refuses with: EXPIRED. When queried about state at height 1200 (beyond its current sync point), it refuses with: OUT_OF_SCOPE. Only queries within [1000, 1100] receive VERIFIED responses.

This explicit scoping enables informed human judgment. Users know precisely what is verified versus what requires additional trust assumptions.

# 9. What zApps Are Not

zApps are intentionally limited. They are not:

- A general-purpose virtual machine—no Turing-complete execution layer

- A replacement for execution-heavy contracts—bounded verification limits complexity

- Atomic across all applications—no global synchronous composability

- Free of latency tradeoffs—proof generation and verification introduce delays

These are not implementation limitations. They are architectural commitments that preserve verifier sovereignty.

Systems that claim to provide unbounded verification, global atomicity, and execution-layer expressiveness simultaneously either (1) require verifiers to match producer resources, eliminating the verification advantage, or (2) introduce hidden trust assumptions that compromise security.

zApps choose explicit constraints over implicit trust.

# 10. Application Classes Enabled by Proof-First Verification

zApps enable application classes impractical under execution-first models:

- Proof-verifiable exchanges where order matching occurs off-chain, verified on-chain

- Verifiable identity attestations with selective disclosure and bounded proof sizes

- Offline-capable financial instruments that can be verified upon reconnection

- Auditable governance systems with cryptographic vote tallying

- Dispute-resilient registries where claims are proven rather than executed

- Censorship-resistant coordination protocols with explicit refusal semantics

In each case, correctness is proven, not trusted. The application producer generates a proof of correct execution. Verifiers check the proof without replaying execution.

This inverts the trust model. Execution-first platforms require trusting the execution environment. Proof-first platforms require trusting only cryptographic primitives and the verifier's own proof-checking logic.

# 11. Relationship to Other Systems

zApps occupy a distinct position in the design space of distributed application platforms. Understanding this position requires examining what other systems assume and what zApps minimize.

Ethereum / EVM: Execution-first model where verification occurs by replaying execution. Verifiers must re-execute every transaction to confirm state transitions. Light clients either trust RPC providers or cannot verify application logic. The cost of verification asymptotically approaches the cost of execution as applications grow complex.

Rollups (Optimistic and Validity): Separate execution from settlement but assume verifiers can access rollup operators or settle disputes on a trusted Layer-1. Light clients must trust rollup sequencers or full nodes to verify rollup state. Bounded verifiers cannot independently verify rollup correctness without operator assumptions.

zkApps (e.g., Mina Protocol): Use succinct proofs for constant-size verification but maintain a global state model. All verifiers observe the same global state. This requires either unbounded resources to track global state or trust assumptions about state roots. The verification is succinct, but the state model remains global.

# Why zApps Minimize Verifier Assumptions:

zApps do not assume:

- Verifiers can replay execution (execution-first assumption)

- Verifiers can access global state (global state assumption)

- Verifiers trust intermediaries (operator/sequencer assumption)

- Verifiers have unbounded resources (resource assumption)

- Applications compose atomically (synchrony assumption)

Instead, zApps assume only:

- Cryptographic hash functions are collision-resistant

Proof systems are sound (invalid proofs are rejected)

- Commitment chains are sequentially ordered

- Verifiers operate within explicitly declared bounds

This minimal assumption set enables verification under resource constraints where other models fail. The trade-off is reduced expressiveness: zApps cannot provide global atomicity or unbounded state access. But for verifiers operating at the edge—browsers, mobile devices, offline nodes—these constraints are unavoidable. zApps acknowledge them architecturally rather than papering over

them with trust assumptions.

zApps minimize verifier assumptions because they prioritize verifier sovereignty over execution expressiveness. This is not an optimization. It is a different architectural goal.

# 12. Open Problems and Future Directions

Several challenges remain for proof-first application architectures:

- Proof availability: How do verifiers obtain proofs when producers are unavailable?

- Developer ergonomics: What programming models make proof generation tractable?

- UX abstractions: How do interfaces communicate refusal semantics clearly?

- Cross-zApp composition: What proof structures enable efficient multi-application verification?

- Human-readable scopes: How do users understand verification boundaries?

These are engineering and design challenges, not conceptual gaps. The architectural model is sound; the tooling ecosystem must catch up.

# 13. Conclusion

zApps are not an optimization of smart contracts. They are a redefinition of what applications mean in systems where verifiers cannot match producer resources.

Traditional platforms assume verification follows from execution: build a virtual machine, replay transactions, verify by re-executing. This model requires verifiers to scale with producers—a requirement that excludes edge participants by construction.

zApps invert the priority. Verification is architecturally primary. Execution is secondary. Applications are defined by what they prove, not what they execute.

As distributed systems move toward browser-native participation, offline-resilient verification, and sovereign light clients, application models must evolve. Execution-first platforms cannot serve verifiers with finite resources. Proof-first platforms can.

zApps represent this evolution. They are necessary—not merely useful—for systems that take verifier sovereignty seriously.