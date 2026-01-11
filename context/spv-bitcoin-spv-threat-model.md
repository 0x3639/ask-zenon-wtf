# Bitcoin SPV Threat Model

**Phase**: 0 — Reference Model & Threat Formalization
**Status**: Exploratory / Research Draft

---

## 1. Purpose

This document formalizes the threat model for Bitcoin SPV verification within Zenon. It identifies adversary capabilities, attack vectors, security assumptions, and defense mechanisms.

Understanding these threats is prerequisite to designing safe verification protocols in subsequent phases.

---

## 2. Adversary Model

### 2.1 Adversary Capabilities

| Capability | Description | Bound |
|------------|-------------|-------|
| Bitcoin hashpower | Fraction of total Bitcoin mining power | $q < 0.5$ |
| Network position | Ability to intercept/delay messages | Partial eclipse |
| Computational resources | CPU/memory for proof generation | Polynomial |
| Economic resources | Funds for attacks | Bounded by stake |

### 2.2 Adversary Goals

1. **Double-spend**: Convince Zenon that a Bitcoin transaction is confirmed, then reverse it on Bitcoin
2. **False inclusion**: Submit proof for a transaction that was never included in Bitcoin
3. **Denial of service**: Overwhelm verifiers with expensive-to-check invalid proofs
4. **Eclipse attack**: Isolate a verifier from honest header sources
5. **Timing attack**: Exploit confirmation threshold during chain reorganization

### 2.3 What the Adversary Cannot Do

- Break SHA256 preimage or collision resistance
- Control > 50% of Bitcoin hashpower sustainably
- Prevent all communication between honest nodes indefinitely

---

## 3. Attack Vectors

### 3.1 False Header Chain Attack

**Description**: Adversary constructs a fake Bitcoin header chain with valid PoW but different transaction history.

**Mechanism**:
1. Mine headers with sufficient PoW
2. Include fake Merkle root committing to desired transaction
3. Submit proof against this fake chain

**Cost**: For $z$ confirmations at difficulty $D$:

$$
\text{Cost} \ge z \times D \times \text{BlockReward}
$$

At current Bitcoin difficulty (~80 EH/s), mining 6 fake blocks costs approximately $\$500,000$ in electricity alone.

**Defense**: Canonical chain verification (Phase 2/3)

### 3.2 Reorganization Race Attack

**Description**: Adversary creates a transaction, waits for $z$ confirmations on Zenon, then mines an alternative Bitcoin chain that excludes the transaction.

**Success Probability**:

$$
P_{\text{success}} \approx \left(\frac{q}{1-q}\right)^z
$$

| $q$ | $z=1$ | $z=6$ | $z=12$ |
|-----|-------|-------|--------|
| 0.10 | 11.1% | 0.0002% | ~0% |
| 0.25 | 33.3% | 0.14% | 0.0002% |
| 0.30 | 42.9% | 0.59% | 0.0035% |

**Defense**: Sufficient confirmation depth requirement

### 3.3 Eclipse Attack

**Description**: Adversary controls all of a verifier's connections to Bitcoin header sources, feeding false chain data.

**Mechanism**:
1. Identify target Zenon node
2. Monopolize its peer connections
3. Serve headers from attacker-controlled chain
4. Target submits proof against false chain

**Requirements**:
- Network-level access to target
- Sufficient fake chain PoW
- Sustained connection monopoly

**Defense**: Threshold relaying from multiple independent sources (Phase 2)

### 3.4 DoS via Oversized Proofs

**Description**: Adversary submits maximally large valid or near-valid proofs to exhaust verifier resources.

**Mechanism**:
1. Construct proofs with maximum header count
2. Include deep Merkle branches
3. Submit many proofs in parallel

**Resource consumption per proof**:
- Storage: ~162 KB
- Computation: ~4000 SHA256 operations
- Verification time: ~1-10 ms

**Defense**:
- Proof size limits (enforced in verifier spec)
- Resource cost borne by submitter (Phase 1)
- Rate limiting on submissions

### 3.5 Merkle Tree Collision Attack

**Description**: Exploit potential weaknesses in Merkle tree construction to forge inclusion proofs.

**Mechanism**: Find a transaction $tx'$ such that it produces the same Merkle root as $tx$ through different branch computation.

**Feasibility**: Requires SHA256 collision, which is computationally infeasible ($2^{128}$ operations).

**Defense**: Inherent SHA256 security

### 3.6 Difficulty Adjustment Exploitation

**Description**: Attack during Bitcoin difficulty adjustment periods when target changes.

**Mechanism**:
1. Observe difficulty adjustment boundary
2. Construct proof spanning adjustment
3. Exploit any inconsistency in target validation

**Defense**:
- Validate difficulty target per-header
- Optional: Validate difficulty adjustment rules (every 2016 blocks)

### 3.7 Timestamp Manipulation

**Description**: Submit headers with manipulated timestamps to affect validation.

**Bitcoin constraints**:
- Timestamp must be > median of last 11 blocks
- Timestamp must be < network time + 2 hours

**Impact on SPV**: Minimal, as SPV verification doesn't depend on absolute timestamps.

**Defense**: Optional timestamp bounds checking

---

## 4. Security Assumptions

### 4.1 Bitcoin Assumptions

| Assumption | Description | Basis |
|------------|-------------|-------|
| Honest majority | $q < 0.5$ hashpower is adversarial | Bitcoin security model |
| SHA256 security | Collision/preimage resistance | Cryptographic hardness |
| Difficulty validity | Bitcoin difficulty reflects real hashpower | Economic incentives |

### 4.2 Zenon Assumptions

| Assumption | Description | Basis |
|------------|-------------|-------|
| Header availability | Honest headers can be obtained | Multiple data sources |
| Verifier correctness | Implementation matches specification | Testing/audit |
| Resource isolation | Malicious proofs don't affect other accounts | Account-chain model |

### 4.3 Network Assumptions

| Assumption | Description | Basis |
|------------|-------------|-------|
| Partial synchrony | Messages eventually delivered | Standard network model |
| Source diversity | Multiple independent header sources exist | Bitcoin network topology |

---

## 5. Defense Mechanisms

### 5.1 Confirmation Depth Selection

**Mechanism**: Require $z$ confirmations proportional to transaction value.

**Recommended thresholds**:

| Value Category | Confirmations ($z$) | Reorg Probability ($q=0.25$) |
|----------------|---------------------|------------------------------|
| Micro (<$100) | 1 | 33% |
| Small (<$10K) | 3 | 3.7% |
| Medium (<$100K) | 6 | 0.14% |
| Large (>$100K) | 12+ | <0.001% |

### 5.2 Header Chain Length Requirements

**Mechanism**: Require proof to include headers beyond the minimum for confirmation depth.

**Rationale**: Longer chains are more expensive to fake.

**Recommendation**: Require $n \ge z + 6$ headers minimum.

### 5.3 Proof Size Limits

**Mechanism**: Enforce maximum bounds on proof components.

| Component | Maximum | Rationale |
|-----------|---------|-----------|
| Headers | 2016 | One difficulty period |
| Merkle depth | 14 | Block size limit |
| Total size | 162 KB | Practical bound |

### 5.4 Threshold Relaying (Phase 2)

**Mechanism**: Accept header tips only if observed from $\ge k$ independent sources.

$$
| \{s_j : \text{tip}(s_j) = \hat{t}\} | \ge k
$$

**Trade-offs**:
- Higher $k$: More eclipse resistance, higher latency
- Lower $k$: Faster confirmation, more eclipse risk

**Recommendation**: $k \ge 3$ with source independence verification.

### 5.5 Optimistic Verification with Fraud Proofs (Phase 3)

**Mechanism**: Accept facts optimistically with challenge window.

**Workflow**:
1. Submitter posts fact with bond
2. Challenge window $T$ opens
3. Challengers can submit fraud proofs (higher-work chain, invalid proof)
4. If challenged successfully, fact reverted and submitter slashed

**Defense against**: False facts reaching global state.

### 5.6 Local Cost Isolation (Phase 1)

**Mechanism**: Verification cost paid by requesting account.

**Defense against**: DoS amplification where attacker's cost is lower than defender's cost.

**Implementation**: Plasma-based resource consumption.

---

## 6. Residual Risks

### 6.1 Accepted Risks

| Risk | Probability | Mitigation | Acceptance Rationale |
|------|-------------|------------|----------------------|
| 6-conf reorg ($q=0.3$) | 0.6% | Higher $z$ for high-value | Standard Bitcoin risk |
| Eclipse (short-term) | Low | Threshold relay | Temporary, recoverable |
| Implementation bugs | Variable | Audit, testing | Standard software risk |

### 6.2 Unmitigated Risks

| Risk | Description | Reason Unmitigated |
|------|-------------|-------------------|
| 51% attack | Sustained majority attack on Bitcoin | Outside Zenon's control |
| SHA256 break | Cryptographic breakthrough | Fundamental assumption |
| Global network partition | Complete isolation | Extreme scenario |

---

## 7. Monitoring Requirements

### 7.1 Real-Time Monitoring

- Bitcoin tip agreement across header sources
- Unusual difficulty variations
- Large-value fact submissions near confirmation threshold

### 7.2 Post-Hoc Analysis

- Reorg frequency and depth on Bitcoin
- Fraud proof submission patterns
- Source reliability metrics

---

## 8. Threat Comparison to Traditional Bridges

| Threat | SPV Approach | Multisig Bridge |
|--------|--------------|-----------------|
| Collusion | Requires $q > 0.5$ Bitcoin hashpower | Requires $t$ of $n$ signers |
| Eclipse | Mitigated by threshold relay | N/A (trusted signers) |
| Key compromise | N/A (no keys) | Single point of failure |
| Verification cost | Paid by requester | Paid by bridge operators |
| Trust assumption | Bitcoin honest majority | Signer honesty |

---

## 9. Summary

The primary security of Bitcoin SPV on Zenon derives from Bitcoin's proof-of-work and the exponential decay of reorg probability with confirmation depth.

Key defenses:
1. **Confirmation depth** — Exponential security increase
2. **Threshold relaying** — Eclipse resistance
3. **Fraud proofs** — Global state protection
4. **Local cost isolation** — DoS resistance

Residual risks are bounded and comparable to standard Bitcoin usage.

---

## 10. References

- [Bitcoin SPV Verifier Specification](bitcoin-spv-verifier-spec.md)
- [Zenon Threat Model](/docs/specs/threat-model.md)
- Karame et al. "Two Bitcoins at the Price of One" (2012)
- Gervais et al. "On the Security and Performance of Proof of Work Blockchains" (2016)
