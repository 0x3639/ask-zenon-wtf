# Bitcoin SPV Test Vectors

**Phase**: 0 — Reference Model & Threat Formalization
**Status**: Exploratory / Research Draft

---

## 1. Purpose

This document provides conformance test vectors for Bitcoin SPV verifier implementations. All conforming implementations must produce identical results for these test cases.

**Acceptance Criterion**: For any proof $\pi$ and threshold $z$, all implementations return identical $V(\pi, z)$.

---

## 2. Notation

- All byte sequences are shown in hexadecimal, little-endian unless noted
- `0x` prefix indicates hexadecimal
- Block hashes displayed in natural (big-endian) format for readability
- Internal computations use little-endian

---

## 3. Header Validation Vectors

### 3.1 Valid Mainnet Header (Block 100,000)

```
Header (hex, 80 bytes):
01000000
50120119172a610421a6c3011dd330d9df07b63616c2cc1f1cd00200000000
6657a9252aacd5c0b2940996ecff952228c3067cc38d4885efb5a4ac4247e9f3
37221b4d
4c86041b
0f2b5710

Parsed fields:
- version: 1
- prev_block: 000000000002d01c1fccc21636b63d9dfd330d31103c6a2104612a17191250
- merkle_root: f3e94742aca4b5ef85488dc37c06c32822955f9ec9609942b2c0d5ac52a957660
- timestamp: 1293623863 (2010-12-29 11:57:43 UTC)
- bits: 0x1b0486c4
- nonce: 274148111

Expected:
- Block hash: 000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506
- Target: 0x00000000000486c4...0000 (derived from bits)
- PoW valid: YES (hash < target)
```

### 3.2 Valid Genesis Block (Block 0)

```
Header (hex, 80 bytes):
01000000
0000000000000000000000000000000000000000000000000000000000000000
3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a
29ab5f49
ffff001d
1dac2b7c

Expected:
- Block hash: 000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
- PoW valid: YES
```

### 3.3 Invalid PoW (Fabricated Header)

```
Header (hex, 80 bytes):
01000000
50120119172a610421a6c3011dd330d9df07b63616c2cc1f1cd00200000000
6657a9252aacd5c0b2940996ecff952228c3067cc38d4885efb5a4ac4247e9f3
37221b4d
4c86041b
00000000  <- Invalid nonce (zeroed)

Expected:
- Block hash: (computed hash > target)
- PoW valid: NO
- Error: E_POW_INVALID
```

### 3.4 Malformed Header (Wrong Size)

```
Header (hex, 79 bytes - missing last byte):
01000000
50120119172a610421a6c3011dd330d9df07b63616c2cc1f1cd00200000000
6657a9252aacd5c0b2940996ecff952228c3067cc38d4885efb5a4ac4247e9f3
37221b4d
4c86041b
0f2b57

Expected:
- Error: E_INVALID_HEADER_SIZE
```

---

## 4. Chain Linkage Vectors

### 4.1 Valid Chain (Blocks 100,000 → 100,001)

```
Header 0 (Block 100,000):
[as above]
Hash: 000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506

Header 1 (Block 100,001):
01000000
06e533fd1ada86391f3f6c343204b0d278d4aaec1c0b20aa27ba0300000000
6abbb3eb3d733a9fe18967fd7d4c117e4ccbbac5bec4d910d900b3ae0793e77f
54241b4d
4c86041b
b5e8a786

Expected:
- Header 1.prev_block == Hash(Header 0): YES
- Chain valid: YES
```

### 4.2 Broken Chain (Mismatched prev_block)

```
Header 0 (Block 100,000):
[as above]

Header 1 (Fabricated - wrong prev_block):
01000000
0000000000000000000000000000000000000000000000000000000000000000  <- Wrong!
6abbb3eb3d733a9fe18967fd7d4c117e4ccbbac5bec4d910d900b3ae0793e77f
54241b4d
4c86041b
b5e8a786

Expected:
- Chain valid: NO
- Error: E_CHAIN_BROKEN
```

---

## 5. Chainwork Computation Vectors

### 5.1 Single Header Work

```
Input:
- bits: 0x1b0486c4

Computation:
- Target T = 0x0486c4 * 2^(8*(0x1b - 3))
           = 0x0486c4 * 2^(8*24)
           = 0x00000000000486c400000000000000000000000000000000000000000000

- Work W = floor(2^256 / (T + 1))
         = 0x50f020c47ce6d0296d0a2b0e9d8c9b0e...

Expected work (decimal): ~4,295,032,833,000 (approximately)
```

### 5.2 Cumulative Chainwork (3 Headers)

```
Input: Headers at blocks 100,000, 100,001, 100,002
All with bits = 0x1b0486c4

Expected:
- W_chain = 3 * W_single
- Cumulative work (decimal): ~12,885,098,499,000
```

### 5.3 Difficulty Adjustment Boundary

```
Input: Headers spanning difficulty adjustment (e.g., blocks 2015, 2016)

Block 2015: bits = 0x1d00ffff (genesis difficulty)
Block 2016: bits = 0x1d00ffff (no change in early blocks)

Expected:
- Each header validated against its own target
- Chainwork sum accounts for different difficulties
```

---

## 6. Merkle Inclusion Vectors

### 6.1 Single Transaction (Coinbase Only)

```
Block with single transaction:
- tx_hash: 0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
- merkle_root: same as tx_hash (single tx case)
- branch: [] (empty)
- positions: [] (empty)

Verification:
- Reconstruct: tx_hash (no siblings)
- Compare to merkle_root: MATCH
```

### 6.2 Two Transactions

```
Block with two transactions:
- tx_0: 0xaaa...
- tx_1: 0xbbb...
- merkle_root: SHA256(SHA256(tx_0 || tx_1))

Proof for tx_1:
- tx_hash: 0xbbb...
- branch: [0xaaa...]
- positions: [1] (tx_1 is on right)

Verification:
- x_0 = 0xbbb...
- x_1 = SHA256(SHA256(0xaaa... || 0xbbb...))
- Compare x_1 to merkle_root: MATCH
```

### 6.3 Eight Transactions (Depth 3)

```
Tree structure:
              root
            /      \
          h01        h23
         /   \      /   \
       h0    h1    h2    h3
       |     |     |     |
      tx0   tx1   tx2   tx3   tx4   tx5   tx6   tx7
                               \     /     \    /
                                h45         h67
                                  \         /
                                    h4567 (padded to 8)

Proof for tx_5:
- tx_hash: hash(tx_5)
- branch: [hash(tx_4), hash(h67), hash(h01)]
- positions: [1, 0, 1]

Verification:
- x_0 = hash(tx_5)
- x_1 = SHA256(SHA256(hash(tx_4) || x_0))  // position[0]=1 means x on right
- x_2 = SHA256(SHA256(x_1 || hash(h67)))   // position[1]=0 means x on left
- x_3 = SHA256(SHA256(hash(h01) || x_2))   // position[2]=1 means x on right
- Compare x_3 to merkle_root
```

### 6.4 Invalid Branch (Wrong Sibling)

```
Proof with corrupted sibling:
- tx_hash: 0xbbb...
- branch: [0x0000...0000]  <- Wrong sibling
- positions: [1]

Expected:
- Reconstructed root != header.merkle_root
- Error: E_MERKLE_MISMATCH
```

### 6.5 Excessive Branch Depth

```
Proof with 15 levels:
- branch: [s_1, s_2, ..., s_15]  <- Exceeds maximum of 14

Expected:
- Error: E_BRANCH_TOO_DEEP
```

---

## 7. Confirmation Depth Vectors

### 7.1 Exactly z Confirmations

```
Input:
- n = 6 (headers 0..6)
- b = 0 (tx in first block)
- z = 6

Calculation:
- depth = n - b = 6 - 0 = 6
- depth >= z: YES

Expected: VALID
```

### 7.2 Below Threshold

```
Input:
- n = 5 (headers 0..5)
- b = 0 (tx in first block)
- z = 6

Calculation:
- depth = 5 - 0 = 5
- depth >= z: NO

Expected:
- Error: E_INSUFFICIENT_DEPTH
```

### 7.3 Transaction in Last Block

```
Input:
- n = 10 (headers 0..10)
- b = 10 (tx in last block)
- z = 1

Calculation:
- depth = 10 - 10 = 0
- depth >= z: NO

Expected:
- Error: E_INSUFFICIENT_DEPTH (need at least 1 confirmation)
```

### 7.4 Deep Confirmation

```
Input:
- n = 100 (headers 0..100)
- b = 0 (tx in first block)
- z = 6

Calculation:
- depth = 100 - 0 = 100
- depth >= z: YES

Expected: VALID (over-confirmed is acceptable)
```

---

## 8. Combined Proof Vectors

### 8.1 Valid Complete Proof

```
Proof package:
- headers: [H_0, H_1, H_2, H_3, H_4, H_5, H_6]  // 7 headers
- tx: 0x1234...
- merkle_branch: [s_1, s_2, s_3]
- b: 0
- z: 6

Verification steps:
1. Structural: n=6 >= b+z=0+6 ✓
2. PoW: All 7 headers valid ✓
3. Linkage: All prev_block fields match ✓
4. Merkle: Reconstructed root matches H_0.merkle_root ✓
5. Depth: 6-0=6 >= 6 ✓

Expected: V(π, 6) = 1
```

### 8.2 Invalid Proof (Each Failure Mode)

| Test Case | Failure | Expected Error |
|-----------|---------|----------------|
| Short chain | n < b + z | E_INSUFFICIENT_DEPTH |
| Bad block index | b > n | E_INVALID_BLOCK_INDEX |
| Wrong header size | len(H_i) != 80 | E_INVALID_HEADER_SIZE |
| PoW failure | hash > target | E_POW_INVALID |
| Broken link | prev_block mismatch | E_CHAIN_BROKEN |
| Merkle fail | root mismatch | E_MERKLE_MISMATCH |
| Deep branch | depth > 14 | E_BRANCH_TOO_DEEP |

---

## 9. Edge Cases

### 9.1 Minimum Valid Proof

```
z = 1, b = 0, n = 1:
- 2 headers required (H_0, H_1)
- tx in H_0
- depth = 1

Expected: VALID (minimum confirmations)
```

### 9.2 Maximum Valid Proof

```
n = 2015 (maximum headers)
b = 0
z = 2015

Expected: VALID (if all checks pass)
```

### 9.3 Empty Transaction

```
tx = 0x00 (minimal)

Expected: Valid if Merkle proof is correct
(Transaction content not validated, only inclusion)
```

### 9.4 Difficulty Adjustment Within Proof

```
Proof spanning blocks 2015, 2016, 2017:
- Block 2015: bits = 0x1d00ffff
- Block 2016: bits = 0x1d00d86a (adjusted)

Expected:
- Each header validated against its own target
- Chain linkage still required
- Chainwork computed correctly for each
```

---

## 10. Reference Implementation Pseudocode

```python
def verify_spv(headers, tx, merkle_branch, b, z):
    n = len(headers) - 1

    # Structural checks
    if n < b + z:
        return (False, "E_INSUFFICIENT_DEPTH")
    if b < 0 or b > n:
        return (False, "E_INVALID_BLOCK_INDEX")
    if len(merkle_branch.siblings) > 14:
        return (False, "E_BRANCH_TOO_DEEP")

    # Validate each header
    prev_hash = None
    for i, header in enumerate(headers):
        if len(header) != 80:
            return (False, "E_INVALID_HEADER_SIZE")

        block_hash = sha256(sha256(header))
        target = decode_target(header[72:76])

        if int.from_bytes(block_hash, 'little') > target:
            return (False, "E_POW_INVALID")

        if prev_hash and header[4:36] != prev_hash:
            return (False, "E_CHAIN_BROKEN")

        prev_hash = block_hash

    # Verify Merkle inclusion
    computed_root = merkle_reconstruct(tx, merkle_branch)
    if computed_root != headers[b][36:68]:
        return (False, "E_MERKLE_MISMATCH")

    return (True, None)
```

---

## 11. Test Vector Files

For implementations requiring machine-readable test vectors, the following JSON format is recommended:

```json
{
  "version": "1.0",
  "vectors": [
    {
      "name": "valid_basic_proof",
      "headers": ["0100000050120119..."],
      "tx_hash": "4a5e1e4b...",
      "merkle_branch": {
        "siblings": ["..."],
        "positions": [0, 1, 0]
      },
      "block_index": 0,
      "confirmations": 6,
      "expected_result": true,
      "expected_error": null
    }
  ]
}
```

---

## 12. References

- [Bitcoin SPV Verifier Specification](bitcoin-spv-verifier-spec.md)
- [Bitcoin Block Explorer](https://blockstream.info/) — Source for mainnet test data
- [BIP 37](https://github.com/bitcoin/bips/blob/master/bip-0037.mediawiki) — Merkle branch format
