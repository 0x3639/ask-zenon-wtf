# Bitcoin SPV Feasibility (Notes)

This note sketches why Bitcoin transaction verification via SPV is *cryptographically possible* within Zenon's ledger model.

Zenon could consume Bitcoin as a unilateral fact oracle: verifying external consensus outputs (finality, ordering, cost) without executing Bitcoin or coordinating bidirectionally.

This demonstrates mathematical feasibility only and is not current functionality, active development, or a implementation commitment.

The cryptographic primitives used are standard Bitcoin SPV constructs; the focus here is on their compatibility with Zenon’s ledger semantics, not on novel cryptography.

---

## What needs to be verified

Define the statement \( S \):

> A Bitcoin transaction \( tx \) is included in the canonical Bitcoin chain and is buried under at least \( z \) blocks of proof-of-work.

Zenon does not need to execute Bitcoin.  
Zenon only needs to verify \( S \) and record it as a fact.

---

## Bitcoin primitives used by SPV

### Proof-of-work headers
Each Bitcoin block header \( H_i \) is valid iff:

\[
\text{SHA256}^2(H_i) \le T_i
\]

where \( T_i \) is the difficulty target encoded in `nBits`.

---

### Cumulative chainwork
Define expected work per block:

\[
W_i = \left\lfloor \frac{2^{256}}{T_i + 1} \right\rfloor
\]

Total chainwork:

\[
W_{\text{chain}} = \sum_i W_i
\]

A verifier selecting the chain with maximal \( W_{\text{chain}} \) can identify the canonical Bitcoin history using **headers only**.

---

### Transaction inclusion (Merkle proof)
Each block header commits to a Merkle root \( R \).

Given:
- transaction hash \( h \)
- Merkle branch \( \pi = (s_1,\dots,s_k) \)

Compute:

\[
x_0 = h
\]

\[
x_j = H(x_{j-1} \| s_j) \;\; \text{(ordering per position)}
\]

Inclusion holds iff:

\[
x_k = R
\]

This requires \( O(\log n) \) hashes and no full block data.

---

### Confirmation security
Let:
- \( q \) = attacker hashpower fraction
- \( p = 1 - q \)
- \( z \) = confirmations

The probability of an attacker catching up from \( z \) blocks behind is bounded by:

\[
P \approx \left(\frac{q}{p}\right)^z \quad (p > q)
\]

Security increases exponentially with depth.

---

## Feasibility conclusion

Using only:
- header PoW verification
- cumulative chainwork
- Merkle inclusion proofs
- confirmation depth

a verifier can deterministically check statement \( S \).

Zenon’s ledger does not need to replicate Bitcoin state or execution to incorporate such verified statements.

---

## Boundary

This note establishes **cryptographic feasibility only**.

It does not address:
- networking
- incentives
- data availability
- protocol activation

Those are engineering and governance questions, not mathematical blockers.
