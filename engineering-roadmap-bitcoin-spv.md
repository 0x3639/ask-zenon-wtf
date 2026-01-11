# Engineering Roadmap — Bitcoin SPV on Zenon (Exploratory RFC)

**Status:** Exploratory / Request for Comment (RFC)  
**Subject:** Cross-Chain Interoperability, Lightweight Client Verification

> **Note:** This document is an exploratory research RFC. It does not represent an official Zenon roadmap, implementation plan, protocol proposal, or commitment by the Zenon team or community.

---

## Abstract

This document outlines a research-driven engineering roadmap for exploring Bitcoin Simplified Payment Verification (SPV) within the Zenon ledger architecture. It proposes a phased approach that prioritizes cryptographic correctness, deterministic verification, and local resource isolation over global consensus changes.

By decoupling verification from execution, this roadmap examines how externally verified Bitcoin facts (transaction inclusion and depth) could be imported into Zenon using a trust-minimized, optimistic checkpointing model. The focus is on architectural feasibility and engineering sequencing, not activation or adoption.

---

## 1. Introduction and Guiding Principles

Integrating external Proof-of-Work (PoW) consensus into another ledger presents a fundamental challenge: how to verify external truth without imposing prohibitive global costs or introducing trusted intermediaries.

This roadmap explicitly avoids traditional “bridge” designs based on multisignature federations or committee attestation. Instead, it explores a math-based SPV approach consistent with Zenon’s dual-ledger architecture.

The engineering path adheres to four binding constraints:

- **Verification ≠ Execution**  
  Zenon verifies cryptographic facts (e.g., Merkle inclusion, PoW headers) but does not execute foreign state machines or scripts.

- **Local Cost Priority**  
  Computationally expensive verification is borne by the specific account requesting it, not the global consensus layer.

- **Determinism First**  
  Correctness and reproducibility must be established before any economic or incentive mechanisms are considered.

- **Optionality Before Consensus Coupling**  
  No feature becomes consensus-critical until its safety properties are validated in isolation.

---

## 2. Methodology and Formal Definitions

### 2.1 External Statement

We define the statement to be verified as:

$$
S(tx, z) := \text{“Bitcoin transaction } tx \text{ is included in the canonical Bitcoin chain and buried under } z \text{ blocks.”}
$$

For clarity, the *canonical Bitcoin chain* is defined as the valid header chain with **maximal cumulative proof-of-work**, as determined by standard Bitcoin consensus rules.

Zenon does not execute Bitcoin logic. It verifies only the cryptographic evidence sufficient to establish $S(tx, z)$.

---

### 2.2 Proof Package

The prover submits a minimal SPV proof package:

$`\pi := (H_{0..n},\; tx,\; \text{merkle}\_\text{branch},\; b)`$

Where:
- $H_{0..n}$: a sequence of Bitcoin block headers
- $tx$: the transaction data or hash
- $`\text{merkle}\_\text{branch}`$: sibling hashes reconstructing the Merkle root
- $b$: index of the block containing $tx$

---

### 2.3 Verification Predicate

The verification function $V(\pi, z) \to \{0,1\}$ evaluates true iff all conditions hold:

- **PoW Validity**

$$
\mathrm{SHA256}^2(H_i) \le T_i
$$

- **Maximal Chainwork**

$$
W_i = \left\lfloor \frac{2^{256}}{T_i + 1} \right\rfloor,\quad
W_{\text{chain}} = \sum_i W_i
$$

- **Merkle Inclusion**

$$
\mathrm{MerkleRoot}(tx,\text{branch}) = R(H_b)
$$

- **Confirmation Depth**

$$
n - b \ge z
$$

**Security Note:**  
For an attacker with hashpower fraction $q < 0.5$, the probability of reversing a transaction decays exponentially:

$$
P_{\text{reorg}} \approx \left(\frac{q}{1-q}\right)^z
$$

This bound applies to the Bitcoin domain and is independent of Zenon.

---

## 3. Engineering Roadmap

The roadmap is divided into six phases (0–5). Each phase delivers a standalone, testable component. Failure or abandonment of later phases does not compromise earlier work.

---

### Phase 0 — Reference Model & Threat Formalization

**Objective:**  
Produce a platform-agnostic, deterministic Bitcoin SPV verifier.

**Deliverables:**
- Header validation and chain linkage
- Chainwork computation and selection
- Merkle inclusion verification
- Confirmation depth checks
- Comprehensive test vectors

**Acceptance Criterion:**  
For any proof $\pi$, all conforming implementations must return identical $V(\pi, z)$.

**Threat Modeling:**
- Eclipse attacks (false header feeds)
- DoS via oversized proofs
- Reorg behavior near confirmation threshold

---

### Phase 1 — Account-Level Verification (Isolation)

**Objective:**  
Validate local cost isolation using Zenon’s account-chain model.

**Mechanism:**  
Introduce an account-chain operation:

VerifyBitcoinSPV(π)

**Cost Isolation:**  
Verification cost is paid by the invoking account using existing resource mechanisms (e.g., Plasma-like credits).

**Resource Bounds:**  
To prevent abuse:

$$
C(\pi) \approx 2h + k \le C_{\max}
$$

where $h$ is header count and $k$ is Merkle branch length.

**Outcome:**  
Only the local account state is updated. Momentum does not re-verify proofs.

---

### Phase 2 — Header Networking & Data Ingestion

**Objective:**  
Mitigate header availability and eclipse risks.

**Option A — Threshold Relaying:**  
Accept a header tip $\hat{t}$ only if observed from at least $k$ independent sources:

$$
| \{s_j : \mathrm{tip}(s_j)=\hat{t}\} | \ge k
$$

This threshold mechanism mitigates eclipse risk but does **not** constitute a separate consensus system or introduce new trust assumptions beyond standard SPV verification.

**Deliverables:**  
A P2P gossip extension or sidecar service aggregating Bitcoin headers.

---

### Phase 3 — Optimistic Checkpointing

**Objective:**  
Provide global visibility of verified facts without global verification cost.

**Mechanism:**  
Checkpoint a lightweight fact:

BTC_FACT(txid, depth, root)

**Workflow:**
1. Local verification (Phase 1)
2. Fact submission to Momentum
3. Challenge window $T$
4. Fraud proof submission (higher-work fork or invalid proof)

Invalid facts are reverted; submitters may be penalized.

---

### Phase 4 — Incentive Mechanisms (Exploratory)

**Objective:**  
Ensure liveness and data availability after correctness is established.

**Models:**
- **Bonded Relayers:** stake $B$, slash $\alpha B$ on invalid data
- **Service Credits:** reward accurate header provision with resource privileges

---

### Phase 5 — Protocol-Level Integration (Speculative)

**Objective:**  
Assess whether SPV verification could become a ledger-native validity predicate.

**Requirements:**
- Governance approval
- Independent security review
- Extended adversarial testing

**Integration Scope:**  
Limited to specific transaction types; no general cross-chain execution.

---

## 4. Discussion

This roadmap departs from traditional bridge designs by isolating heavy verification at the edge while preserving core ledger scalability. Optimistic checkpointing enables Zenon to reason about Bitcoin facts without forcing every node to process Bitcoin data.

---

## 5. Conclusion

This document presents a mathematically grounded, phased engineering path for exploring Bitcoin SPV within Zenon. It moves from formal definitions to localized execution and optional global visibility, while respecting Zenon’s architectural constraints.

No assumptions are made regarding activation, timelines, or adoption.  
The roadmap exists to enable informed technical discussion, not to prescribe a development path.
