# Minimal State Frontier Verification

# (Draft — Final Revision)

Status: Exploratory research

Scope: Verification models, light clients, deterministic state commitments

Non-claim: This document does not describe a deployed protocol or implementation.

# Abstract

This note formalizes minimal state frontier verification: a verification model in which a verifier with bounded memory tracks only a subset of state commitments (the frontier) sufficient to ensure local temporal consistency without storing full state or replaying transaction history.

The model identifies what must be retained by a light verifier to prevent acceptance of contradictory proofs across time, while keeping storage costs bounded and device-feasible.

This work establishes an impossibility boundary: no bounded-memory verifier can guarantee global consistency without additional assumptions. The model guarantees only local temporal coherence within the verifier's retained frontier.

# 1. Motivation

Bounded inclusion verification establishes that a verifier can confirm local state facts using header-committed proofs without full execution. However, spatial verification alone does not address temporal consistency.

Consider a verifier that validates proofs independently at times  $t_1$  and  $t_2$ . Without retained state, the verifier cannot detect if these proofs reference mutually inconsistent histories.

If a verifier discards commitment history, it may:

- accept proofs from divergent forks as if coherent

- fail to detect rollback within its verification window

- lose ability to reason about state evolution

If a verifier retains all commitments, storage grows unbounded and device-feasibility is lost.

This note formalizes the minimal retention boundary: what must be remembered to ensure accepted proofs remain coherent within the verifier's local view, without claiming global consistency guarantees.

# 2. Problem Statement

Let a ledger evolve through a sequence of committed state roots:

R_0,R_1,R_2,  $\backslash$  Idots

A light verifier observes:

- headers containing commitments  $R\_i$

- proofs  $\mathsf{L}p\mathsf{i}$  asserting local state facts

The verifier does not:

- store full state S_i

- replay transactions

- enumerate global state changes

- communicate with other verifiers

# Question

What minimal subset of historical commitments must a single verifier retain to ensure that proofs it accepts do not contradict each other within its own verification history?

# Scope Limitation

This question addresses single-verifier temporal coherence. It does not address multi-verifier consensus, global state validity, or detection of state changes outside the verifier's observation window.

# 3. Definitions

# 3.1 State Commitment

A state commitment  $R\_i$  is a collision-resistant digest binding to ledger state at height  $i$ .

# Assumption:

R_i = \text{Commit}(S_i)

where  $S\_i$  is the full ledger state and  $\text{\\text{Commit}}$  is a cryptographic hash function. Collision resistance ensures distinct states yield distinct commitments with overwhelming probability.

# 3.2 Local Proof

A local proof  $\mathsf{p}i$  asserts a predicate  $P$  over a subset of state s  $\backslash$  subset S_i, verifiable against R_i without access to S_i.

# Examples:

- Merkle proof of account balance

Inclusion proof of a specific state transition

Non-membership proof for a key

Verification of  $\mathsf{lp}i$  requires only  $R_{-}i$  and the proof data, not full state.

# 3.3 Frontier (Terminology Clarification)

The state frontier  $F$  is the minimal verifier-retained state needed to validate temporal consistency of future proofs.

At minimum,  $F$  must contain:

- the latest accepted commitment  $R\_ \{\text{text}\{tip\}\}$

commitments needed to verify chain ancestry

The term 'frontier' refers specifically to the temporal boundary of retained commitments required for consistency checking. It is distinct from:

Partial state sync: Synchronizing subsets of state data (accounts, storage). The frontier contains no state data—only commitment hashes.

Checkpointing: Episodic trust anchors from social consensus. The frontier is maintained continuously via cryptographic proofs.

Stateless verification: Independent per-block verification. Frontier verification explicitly retains inter-block commitment history.

# 4. Naïve Strategies and Failure Modes

# 4.1 Stateless Verification (Inadequate)

A verifier accepting proofs independently without retained commitments cannot detect contradictory histories.

Counterexample: Given two proofs  $\mathsf{p}i_{-1}$  claiming  $s = x$  under  $R_{-}1$  and  $\mathsf{p}i_{-2}$  claiming  $s = y$  under  $R_{-}2$  where  $x\backslash \text{neq} y$ , a stateless verifier validates each independently. If  $R_{-}1$  and  $R_{-}2$  reference divergent forks, the verifier accepts contradictory states without detection.

Formally:

\exists exists \pi i 1, \pi i 2 : \text{Verify}(\pi i 1, R 1) \land \text{Verify}(\pi i 2, R 2) \land

(R 1, R 2 \text{on divergent chains})\land

$\backslash \mathrm{pi}1\backslash \mathrm{vdash}s = x)\backslash \mathrm{land}\backslash \mathrm{pi}2\backslash \mathrm{vdash}s = y)\backslash \mathrm{land}x\backslash \mathrm{neg}y$

# 4.2 Full History Retention (Infeasible)

- Storing all commitments  $R_0$  Vdots  $R_n$  ensures consistency but violates bounded-memory requirements. Storage grows  $O(n)$  with chain length, making device deployment infeasible.

# 5. Impossibility Boundary

We establish what cannot be achieved by bounded-memory verifiers.

# 5.1 Information-Theoretic Limitation

# Claim:

No verifier with memory bounded by  $k$  commitments can guarantee detection of all inconsistencies in a history of length  $n > k$  without additional assumptions.

# Argument:

Consider a verifier that retains  $k$  most recent commitments. An adversary presents a proof  $\mathsf{p}i$  at time  $t$  referencing commitment  $R$ $\{t - k - 1\}$  which the verifier has discarded.

The adversary can present  $R_{-}^{\prime}\{t - k - 1\}$  req  $R_{-}\{t - k - 1\}$  (a forged historical root) along with a valid-looking chain from  $R_{-}^{\prime}\{t - k - 1\}$  to some  $R_{-}\{t - j\}$  still in the frontier, where  $j \lor q k$ .

The verifier cannot distinguish the authentic  $R_{-}\{t - k - 1\}$  from  $R_{-}'\{t - k - 1\}$  because it has no record of the former. Under collision resistance alone, both commitments are equally plausible.

Therefore: detection of all historical inconsistencies requires either unbounded memory (contradicting device-feasibility) or additional out-of-band verification (checkpoints, finality, etc.).

# 5.2 What This Means for the Model

Minimal frontier verification guarantees temporal coherence only within the retention window  $k$ . Proofs referencing commitments older than the frontier cannot be verified for consistency with verifier history.

# Consequence:

The model does not claim to prevent all equivocation—only equivocation within the tracked frontier. States outside the frontier are unverifiable against verifier history absent external trust.

# 6. Minimal Frontier Invariant

# Invariant:

A verifier retains sufficient commitment history to ensure that every accepted proof references a state reachable from a previously accepted state via a cryptographically verifiable commitment chain within the retained frontier.

Formally, for proofs accepted at times  $i < j$  within retention window  $k$ :

\text{Accept}(\pi_i, R_i) \land \text{Accept}(\pi_j, R_j) \land \text{(j - i)} \leq k)

\Rightarrow \exists exists! \text{canonical chain} C: R_i \in C \land R_j \in C

where:

-  $C$  is a sequence of headers linking  $R_i$  to  $R_j$ .

-  $F$  is the verifier's current frontier

-  $\text{[Verify]\_Chain}$  checks cryptographic ancestry via parent hashes

Critical qualifier: This invariant applies only to proofs within the retention window. Proofs referencing commitments outside the frontier ( $j - i > k$ ) cannot be verified for consistency with prior verifier state.

# 7. Concrete Instantiation (Chain-Agnostic)

# 7.1 Data Structures

# Header:

structHeader{

height: uint64,

parent_hash: Hash,

state_root: Hash,

timestamp: uint64,

}

The state_root field is  $R_i$  from the abstract model. parent_hash enables ancestry verification.

# State Proof:

```rust
struct StateProof {
    target_root: Hash,
    key:_stateKey,
    value:/stateValue,
    merkle_path: []Hash,
}
```

Verification: recompute root from \text{leaf}(\text{key}), \text{value}) and merkle_path. Accept iff computed root matches target_root.

# Frontier:

```swift
struct Frontier {
    tip: Header,
    retainedheaders: [Header // size bounded by k]
}
```

Parameter  $k$  represents reorganization tolerance. Typical values:  $k = 6$  (probabilistic finality),  $k = 100$  (no finality guarantees).

# 7.2 Verification Algorithm

To verify proof  $\backslash p i$  against frontier  $F$ :

1. Locate header h  $\text{in} F$  where h\.text{state\_root} =  $\text{pi}$ \.text{target\_root}

2. If no such  $h$  exists, reject (target root not in frontier)

3. Verify ancestry: trace parent_hash links from F.\text{tip} to h

4. If ancestry verification fails, reject (orphaned/forked commitment)

5. Verify  $\backslash p i . \backslash t e x t\{\text{merkle\_path}\}$  authenticates ( $\backslash$ text{key},  $\backslash$ text{value}) under  $\backslash p i . \backslash t e x t\{\text{target\_root}\}$

6. Accept iff all checks pass

# 7.3 Frontier Update

On accepting new header  $h'$ :

1. If \( h'.\text{text}\{\text{height}\} > F \). \text{text}\{\text{tip}\}. \text{text}\{\text{height}\} \), set \( F \). \text{text}\{\text{tip}\} = h' \)

2. Prune headers where h\.text{height} < (F\.text{tip}.text{height} - k)

3. Retain headers within [F.\text{tip}].\text{height} - k, F.\text{tip}. \text{height}]

Invariant maintenance: Any proof referencing h\.text{state\_root} where h\.text{height}  $\backslash$  geq (F\.text{tip}.  $\backslash$  text{height} - k) can be verified for consistency with all previously accepted proofs within the same window.

# 8. Verification Walkthrough (Diagram)

This section illustrates frontier-based verification through a concrete sequence.

# 8.1 Initial State

Assume  $k = 3$  (retain 3 most recent headers).

Chain state:

Height: 78910

Header: H7←H8←H9←H10

Root: R7 R8 R9 R10

Frontier:  $F = \{\text{文本}\}$ : H_10,  $\text{文本}$  retained: [H_8, H_9, H_10]

$(H\_ 7$  pruned as height  $7 <   10 - 3)$

# 8.2 Accept Valid Proof

Proof  $\mathsf{p}i_{-9}$  arrives with target_root  $= R_{-9}$

# Verification steps:

1. Locate H_9 in retained Headers  $\checkmark$

2. Verify ancestry: \( H\_ \{10\} \). \text{text{parent}} = H\_ 9 \). \text{text{hash}} \(\checkmark\)

3. Verify merkle_path authenticates data under R_9√

Result: Accept  $\backslash p i_{-}9$

# 8.3 Reject Forked Proof

Proof  $\varphi i_{-}9$  arrives with target_root  $= R^{\prime}_{-}9$  (alternative fork at height 9).

# Attempted verification:

1.  $R_{-}9$  not in any retained header  $\mathcal{X}$

Result: Reject  $\backslash p i^{\prime \prime}9$  (unknown commitment)

Even if adversary provides header  $H'_9$  with state_root =  $R'_9$ , ancestry check fails:

H{10}.text{parent} \neq q H' 9. text{hash} X

Result:  $H'_9$  not on main chain, proof rejected

# 8.4 Cannot Verify Old Proof

Proof  $\mathsf{p}i\_ 7$  arrives with target_root  $= R_{-}7$  (outside frontier).

# Verification attempt:

1. R_7 not in retainedheaders (H_7 was pruned) x

2. Cannot verify consistency with current frontier  $X$

Result: Reject  $\backslash p i_7$  (commitment outside retention window)

Critical observation: This is not a security failure—it is expected behavior under bounded memory. The verifier cannot distinguish authentic  $R\_7$  from a forgery  $R'_7$  without retained history.

# 8.5 Property Demonstrated

All accepted proofs ( $\mathsf{p}i$ -9 referencing  $R$ -9) are mutually consistent within the frontier window. Forked histories ( $\mathsf{p}i$ -9 on  $R$ -9) are rejected. Proofs outside the window ( $\mathsf{p}i$ -7 on  $R$ -7) are unverifiable.

# 9. Frontier Size Bounds

In linear commitment chains with parent hashes, the frontier requires:

F = \{ R_{}\text{tip}\}, k\text{most recent headers}\}

# Storage complexity:

O(1)\text{current tip} + O(k)\text{retained headers}

For hash size  $h = 32$  bytes and header metadata  $m = 64$  bytes, total storage is approximately  $k$  times  $(h + m)$  bytes.

For  $k = 100$ , this is ~10KB—feasible for browser environments.

In DAG-structured chains, storage may increase to  $O(k \times \text{times} \times \text{text} \backslash_{\text{branching\_factor}})$  but remains bounded.

# 10. Multi-Verifier Divergence

Two honest verifiers operating independently may maintain different frontiers and accept different proof histories. This is expected behavior, not a model failure.

# 10.1 Why Divergence Occurs

# Reason 1: Observation timing

- Verifier V_1 observes headers [H_8, H_9, H_10] while V_2 observes [H_9, H_10, H_11]. If proof  $\text{p}i$  references R_8, V_1 accepts while V_2 rejects (R_8 outside frontier).

# Reason 2: Network partition

During a fork,  $V\_1$  observes chain A  $[H\_ \{10\}^{\wedge}A, H\_ \{11\}^{\wedge}A]$  while  $V\_2$  observes chain B  $[H\_ \{10\}^{\wedge}B, H\_ \{11\}^{\wedge}B]$ . Each verifier maintains internal consistency but on divergent histories.

# Reason 3: Proof availability

If proofs are selectively withheld or delivered, verifiers may accept different subsets of valid proofs even when observing the same headers.

# 10.2 What the Model Guarantees Despite Divergence

Each individual verifier guarantees:

Local temporal coherence: All proofs accepted by verifier  $V$  reference commitments on a single consistent chain within  $V$ 's frontier.  $V$  cannot be made to accept contradictory proofs referencing divergent forks simultaneously.

Bounded equivocation detection: Within retention window  $k$ , if an adversary attempts to present proofs from incompatible histories, the verifier rejects at least one.

The model does NOT guarantee:

Cross-verifier agreement: Two verifiers may reach different conclusions about proof validity without communication.

Global consistency: A proof accepted by one verifier may reference state transitions never observed by another verifier.

# 10.3 Convergence Conditions

Verifier frontiers converge when:

Fork resolution: Competing chains are abandoned and all verifiers observe the same canonical chain for  $k$  consecutive blocks.

Finality: An external finality mechanism (proof-of-stake finality gadget, checkpoint authority) designates a canonical history that all verifiers adopt.

Without these conditions, divergence persists. This is inherent to bounded-memory verification and cannot be resolved by model modifications alone.

# 11. Relation to Bounded Inclusion

Bounded inclusion verification addresses:

$>$  "Does this proof correctly demonstrate a state fact under a given commitment?"

Minimal frontier verification addresses:

> "Is this commitment consistent with my verification history?"

Combined, they provide:

- Spatial correctness: proofs correctly reference committed state

- Temporal coherence: commitments form a consistent history within the verifier's view

Neither mechanism alone nor both together guarantee global state validity without additional trust assumptions.

# 12. Comparison with Existing Models

# 12.1 Bitcoin SPV

State retained:

- All block headers from genesis (or checkpoint) to present

- Unbounded growth:  $O(n)$  with chain length

# Detectable failures:

- Transaction not included in presented chain

- Chain with insufficient proof-of-work

# Silent failures:

- Hidden longer fork (if adversary controls network view)

- State transition validity (SPV does not verify state)

# Guarantee scope:

- Local: transaction inclusion in observed chain

- Global: none—does not verify canonical chain selection

# 12.2 Ethereum Light Clients

# State retained:

- Sync committee signatures (1-2 periods,  $\sim 27 - 54$  hours)

- Recent block headers within sync period

- Bounded: O(\text{sync\_period\_length})

# Detectable failures:

- Invalid sync committee signature

- State proof not matching committed root

# Silent failures:

- Finality reversion beyond sync period

- Slashing-induced chain reorganization (until finalized)

# Guarantee scope:

- Local: state consistency with signed committee attestations

- Global: canonical chain per cryptoeconomic finality (relies on validator honesty)

# 12.3 Optimistic Rollups

# State retained:

- Latest rollup state root posted to L1

- No inter-commitment history

# Detectable failures:

- Invalid state transition (via fraud proof during challenge window)

- State proof not matching posted root

# Silent failures:

- Invalid state root if unchallenged

Censorship of fraud proofs

# Guarantee scope:

- Local: state consistency with posted root (assumes validity until proven otherwise)

- Global: eventual consistency (assumes rational challengers and L1 availability)

# 12.4 Stateless Clients (Ethereum Context)

# State retained:

- Current block header only

- No inter-block state

# Detectable failures:

- Witness data not matching block state root

- Invalid state transition within presented block

# Silent failures:

- Acceptance of proofs from divergent forks across blocks

- Rollback or equivocation between verification sessions

# Guarantee scope:

- Local: per-block state validity only

- Global: none—no temporal consistency checking

# 12.5 Minimal Frontier Verification

# State retained:

-  $k$  most recent headers (bounded by reorganization tolerance)

- Bounded:  $O(k)$ , typically 10-100 KB

# Detectable failures:

Proof referencing commitment outside retained frontier

- Proof referencing orphaned/forked commitment within frontier

- Equivocation within retention window  $k$

# Silent failures:

State changes outside retention window

- Equivocation beyond  $k$  blocks in the past

- Global state invalidity (does not verify state transitions)

- Censorship or selective proof availability

# Guarantee scope:

- Local: temporal coherence of accepted proofs within retention window

- Global: none—no cross-verifier consistency or global state validity claims

# 13. Adversarial Considerations

# This model does NOT prevent:

Censorship of proofs or headers

- Hidden state changes outside the verifier's observation

- Selective proof availability attacks

- Long-range attacks beyond retention window  $k$

- Sybil attacks presenting disjoint frontiers

# This model DOES prevent:

- Equivocation within the same verifier's retained frontier

- Acceptance of proofs from incompatible forks within window  $k$

- Silent acceptance of contradictory state claims within tracked history

Scope boundary: The model addresses single-verifier temporal coherence under bounded memory. It does not address network-level adversaries, consensus security, or global consistency without additional assumptions.

# 14. Implications

Minimal state frontier verification enables:

- Bounded-memory light clients deployable in resource-constrained environments

- Temporal consistency checking without full node operation

- Composable state proofs with inter-proof coherence guarantees

- Predictable storage requirements:  $O(k)$  regardless of chain length

The model identifies memory, not computation, as the binding constraint for device-feasible light verification with temporal consistency.

Non-implication: This model does not enable global consistency verification, Byzantine fault tolerance, or canonical chain selection without additional mechanisms (finality, checkpoints, social consensus).

# 15. Open Questions

- What is the minimal  $k$  under varying fork frequencies and finality assumptions?

- Can frontier compression reduce storage while preserving guarantees?

- Under what conditions can divergent verifiers provably converge?

- How do DAG-structured commitment chains affect frontier size bounds?

- Can the impossibility boundary be tightened with specific cryptographic assumptions?

# 16. Core Invariant (Final Formulation)

We restate the model's central guarantee in its tightest form.

# 16.1 Single-Verifier Temporal Coherence

# Guarantee:

A verifier  $V$  with retention parameter  $k$  that accepts proofs  $\backslash p_i\_ 1$  ,  $\backslash p_i\_ 2$  , Vdots,  $\backslash p_i\_ n$  ensures:

\forallforall i, j : \text{Accept}(\backslashpi_i, R_i, t_j) \land \text{Accept}(\backslashpi_j, R_j, t_j) \land

[\text{height}\{R_{i}\} - \text{height}\{R_{j}\} ]  $\text{leg} k$

\Rightarrow \exists exists! \text{canonical chain} C : R_i \in C \land R_j \in C

Where:

-  $C$  is the unique ancestor chain verified via parent hashes

- Both  $R\_i$  and  $R\_j$  lie on  $C$  (no divergent forks)

- The guarantee applies only within the retention window  $k$

# 16.2 Excluded Guarantees (Explicit)

The invariant does NOT guarantee:

Global validity: That states  $S_i, S_j$  are correctly derived from prior states via valid transitions.

Cross-verifier agreement: That another verifier  $V^{\prime}$  accepts the same proofs or maintains the same frontier.

Temporal coherence outside k: That proofs referencing  $R\_x$  where  $|\backslash \text{text}\{\text{height}\}(R\_x) - \backslash \text{text}\{\text{height}\}(R\_ \{\text{text}\{\text{tip}\})\}| > k$  are consistent with V's history.

Completeness: That all valid proofs are accepted (adversary may withhold proofs or headers).

# 16.3 Implementability

This invariant is implementable via the concrete instantiation (Section 7) without modification. The verification algorithm (7.2) and frontier update procedure (7.3) are sufficient to maintain this guarantee.

Every claim in this paper derives from this invariant or explicitly states its limitation relative to it.

# 17. Conclusion

Light verification with temporal consistency is neither stateless nor requires unbounded history. A bounded frontier suffices for local coherence.

Minimal state frontier verification formalizes the smallest retention boundary that preserves single-verified temporal coherence under bounded memory constraints. The model provides well-defined guarantees within the retention window  $k$  and explicitly identifies what cannot be achieved without additional trust assumptions.

This work complements bounded inclusion verification and establishes the information-theoretic limits of header-based light client architectures. Extensions requiring global consistency, cross-verifier agreement, or Byzantine fault tolerance necessitate mechanisms beyond this model's scope.