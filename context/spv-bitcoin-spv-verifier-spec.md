# Bitcoin SPV Verifier Specification

**Phase**: 0 — Reference Model & Threat Formalization
**Status**: Exploratory / Research Draft

---

## 1. Scope

This specification defines a platform-agnostic, deterministic Bitcoin SPV verifier. The verifier accepts a proof package and returns a binary decision: the proof is valid or invalid.

**Determinism Guarantee**: For any proof package $\pi$ and confirmation threshold $z$, all conforming implementations must return identical results for $V(\pi, z)$.

---

## 2. Statement to Verify

The verifier establishes the truth of statement $S$:

$$
S(tx, z) := \text{"Bitcoin transaction } tx \text{ is included in the canonical Bitcoin chain and buried under } z \text{ blocks."}
$$

The *canonical Bitcoin chain* is defined as the valid header chain with **maximal cumulative proof-of-work**, per standard Bitcoin consensus rules.

Zenon does not execute Bitcoin logic. It verifies only the cryptographic evidence sufficient to establish $S(tx, z)$.

---

## 3. Data Structures

### 3.1 Bitcoin Block Header

Each Bitcoin block header is exactly 80 bytes:

| Field | Size | Description |
|-------|------|-------------|
| version | 4 bytes | Block version number |
| prev_block | 32 bytes | Hash of previous block header |
| merkle_root | 32 bytes | Root of transaction Merkle tree |
| timestamp | 4 bytes | Unix timestamp |
| bits | 4 bytes | Encoded difficulty target |
| nonce | 4 bytes | Proof-of-work nonce |

**Block Hash**: The block hash is computed as:

$$
\text{BlockHash}(H) = \text{SHA256}(\text{SHA256}(H))
$$

where $H$ is the 80-byte header. The result is interpreted as a 256-bit little-endian integer.

### 3.2 Difficulty Target

The `bits` field encodes the difficulty target $T$ in compact format:

$$
T = \text{mantissa} \times 2^{8 \times (\text{exponent} - 3)}
$$

where:
- `exponent` = first byte of `bits`
- `mantissa` = remaining 3 bytes (little-endian)

### 3.3 Merkle Branch

A Merkle branch proves transaction inclusion:

| Field | Type | Description |
|-------|------|-------------|
| tx_hash | 32 bytes | Transaction hash (double SHA256) |
| siblings | array of 32 bytes | Sibling hashes at each tree level |
| positions | array of bits | Left (0) or right (1) position at each level |

The maximum branch depth for Bitcoin is $\lceil \log_2(\text{max\_txs}) \rceil$. For blocks up to 4MB, this is approximately 14 levels.

### 3.4 Proof Package

The complete proof package submitted to the verifier:

$$
\pi := (H_{0..n},\; tx,\; \text{merkle\_branch},\; b)
$$

| Component | Description |
|-----------|-------------|
| $H_{0..n}$ | Sequence of $n+1$ Bitcoin block headers |
| $tx$ | Transaction data or hash |
| merkle_branch | Merkle inclusion proof |
| $b$ | Index of the block containing $tx$ (0-indexed) |

---

## 4. Verification Functions

### 4.1 Header PoW Validity

A header $H_i$ satisfies proof-of-work iff:

$$
\text{BlockHash}(H_i) \le T_i
$$

where $T_i$ is the difficulty target extracted from $H_i.\text{bits}$.

**Implementation Note**: The comparison is performed on 256-bit unsigned integers in little-endian byte order.

### 4.2 Header Chain Linkage

Headers form a valid chain iff for all $i \in [1, n]$:

$$
H_i.\text{prev\_block} = \text{BlockHash}(H_{i-1})
$$

### 4.3 Chainwork Computation

Work contributed by a single header:

$$
W_i = \left\lfloor \frac{2^{256}}{T_i + 1} \right\rfloor
$$

Cumulative chainwork for the header sequence:

$$
W_{\text{chain}} = \sum_{i=0}^{n} W_i
$$

**Precision Note**: This computation requires arbitrary-precision integer arithmetic. Implementations must not use floating-point approximations.

### 4.4 Merkle Root Reconstruction

Given transaction hash $h$ and Merkle branch $(s_1, \ldots, s_k)$ with positions $(p_1, \ldots, p_k)$:

$$
x_0 = h
$$

$$
x_j = \begin{cases}
\text{SHA256}(\text{SHA256}(x_{j-1} \| s_j)) & \text{if } p_j = 0 \\
\text{SHA256}(\text{SHA256}(s_j \| x_{j-1})) & \text{if } p_j = 1
\end{cases}
$$

The reconstructed Merkle root is $x_k$.

### 4.5 Confirmation Depth

Confirmation depth of a transaction in block $b$ given a chain of $n+1$ headers:

$$
\text{depth} = n - b
$$

A transaction is considered confirmed at depth $z$ iff:

$$
n - b \ge z
$$

---

## 5. Verification Predicate

The verification function $V(\pi, z) \to \{0, 1\}$ returns 1 (valid) iff ALL of the following conditions hold:

### 5.1 Structural Validity

- Header count: $n \ge b + z$ (sufficient depth)
- Block index: $0 \le b \le n$ (valid range)
- All headers are exactly 80 bytes
- Merkle branch depth $\le 14$ (practical limit)

### 5.2 PoW Validity

For all $i \in [0, n]$:

$$
\text{BlockHash}(H_i) \le T_i
$$

### 5.3 Chain Linkage

For all $i \in [1, n]$:

$$
H_i.\text{prev\_block} = \text{BlockHash}(H_{i-1})
$$

### 5.4 Merkle Inclusion

$$
\text{MerkleReconstruct}(tx, \text{merkle\_branch}) = H_b.\text{merkle\_root}
$$

### 5.5 Confirmation Depth

$$
n - b \ge z
$$

---

## 6. Verification Algorithm

```
FUNCTION Verify(π, z):
    (headers, tx, merkle_branch, b) = π
    n = len(headers) - 1

    # Structural checks
    IF n < b + z THEN RETURN 0
    IF b < 0 OR b > n THEN RETURN 0
    IF len(merkle_branch.siblings) > 14 THEN RETURN 0

    # Verify each header
    FOR i = 0 TO n:
        H = headers[i]
        IF len(H) != 80 THEN RETURN 0

        target = DecodeTarget(H.bits)
        hash = SHA256(SHA256(H))
        IF hash > target THEN RETURN 0

        IF i > 0:
            IF H.prev_block != SHA256(SHA256(headers[i-1])) THEN RETURN 0

    # Verify Merkle inclusion
    computed_root = MerkleReconstruct(tx, merkle_branch)
    IF computed_root != headers[b].merkle_root THEN RETURN 0

    # Verify confirmation depth
    IF n - b < z THEN RETURN 0

    RETURN 1
```

---

## 7. Error Codes

| Code | Description |
|------|-------------|
| E_INSUFFICIENT_DEPTH | Header chain too short for required confirmations |
| E_INVALID_BLOCK_INDEX | Block index out of range |
| E_INVALID_HEADER_SIZE | Header not exactly 80 bytes |
| E_POW_INVALID | Block hash exceeds difficulty target |
| E_CHAIN_BROKEN | Previous block hash mismatch |
| E_MERKLE_MISMATCH | Reconstructed root doesn't match header |
| E_BRANCH_TOO_DEEP | Merkle branch exceeds maximum depth |

---

## 8. Determinism Requirements

### 8.1 Byte-Exact Encoding

- All hashes computed on raw bytes, not hex strings
- Little-endian byte order for all integer comparisons
- No whitespace or formatting variations in serialization

### 8.2 Arithmetic Precision

- Chainwork computation requires 256-bit or arbitrary-precision integers
- No floating-point arithmetic in any verification step
- Division rounds toward zero (floor division)

### 8.3 Hash Function

- SHA256 as specified in FIPS 180-4
- Double-SHA256: $\text{SHA256}(\text{SHA256}(x))$
- No salt, no personalization

---

## 9. Resource Bounds

To prevent denial-of-service attacks, implementations should enforce:

### 9.1 Proof Size Limits

| Parameter | Maximum | Rationale |
|-----------|---------|-----------|
| Header count ($n$) | 2016 | One difficulty period |
| Merkle branch depth | 14 | ~16K transactions per block |
| Total proof size | ~162 KB | Headers + branch + tx |

### 9.2 Computation Complexity

Verification cost approximation:

$$
C(\pi) \approx 2(n+1) + k
$$

where:
- $n+1$ = number of headers (2 SHA256 ops each for hash + link check)
- $k$ = Merkle branch length (2 SHA256 ops each)

For maximum-size proofs: $C \approx 4046$ SHA256 operations.

---

## 10. Canonicality Note

This verifier checks **syntactic validity** of a proof against a submitted header chain. It does **not** establish that the submitted chain is the canonical Bitcoin chain (the chain with maximal cumulative work).

Canonicality assurance requires:

1. Comparing against known checkpoints, OR
2. Receiving headers from multiple independent sources, OR
3. Tracking cumulative chainwork against competing tips

These mechanisms are addressed in Phase 2 (Header Networking) and Phase 3 (Optimistic Checkpointing).

---

## 11. Security Bound

For an attacker with hashpower fraction $q < 0.5$, the probability of reversing a confirmed transaction decays exponentially:

$$
P_{\text{reorg}} \approx \left(\frac{q}{1-q}\right)^z
$$

| Confirmations ($z$) | $q = 0.1$ | $q = 0.3$ |
|---------------------|-----------|-----------|
| 1 | 11.1% | 42.9% |
| 6 | 0.0002% | 0.6% |
| 12 | ~0% | 0.004% |

This bound applies to the Bitcoin domain and is independent of Zenon.

---

## 12. References

- [Bitcoin SPV Feasibility](/docs/notes/bitcoin-spv-feasibility.md)
- [Bitcoin Developer Reference: Block Headers](https://developer.bitcoin.org/reference/block_chain.html)
- [BIP 37: Merkle Branch Verification](https://github.com/bitcoin/bips/blob/master/bip-0037.mediawiki)
- Nakamoto, S. "Bitcoin: A Peer-to-Peer Electronic Cash System" (2008), Section 8
