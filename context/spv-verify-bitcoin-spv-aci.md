# VerifyBitcoinSPV ACI Specification

**Phase**: 1 — Account-Level Verification (Isolation)
**Status**: Exploratory / Research Draft

---

## 1. Overview

This specification defines the `VerifyBitcoinSPV` Application Contract Interface (ACI) for Zenon. The ACI enables accounts to verify Bitcoin transaction inclusion proofs and record verified facts in their account-chain state.

**Key Properties**:
- Verification cost is borne by the invoking account
- Only local account state is updated
- Momentum does not re-verify proofs
- Follows the Deterministic Fact Acceptance (DFA) model

---

## 2. Design Principles

### 2.1 Local Cost Isolation

All computational work for SPV verification is charged to the invoking account's Plasma. This prevents:
- DoS amplification attacks
- Subsidization of expensive verification by other accounts
- Global consensus overhead for local verification

### 2.2 Verification Without Execution

The ACI verifies cryptographic facts about Bitcoin. It does NOT:
- Execute Bitcoin scripts
- Validate transaction semantics
- Interpret transaction outputs
- Track Bitcoin UTXO state

### 2.3 Fact Commitment

Upon successful verification, a structured fact is recorded in the account's state. This fact can be:
- Referenced by subsequent transactions
- Used as input to other ACIs
- Exported via state proof bundles

---

## 3. Interface Definition

### 3.1 Method Signature

```
VerifyBitcoinSPV(
    headers:       bytes[],      // Array of 80-byte Bitcoin headers
    tx_hash:       bytes32,      // Bitcoin transaction hash
    merkle_branch: MerkleBranch, // Inclusion proof
    block_index:   uint16,       // Index of block containing tx
    min_depth:     uint16        // Required confirmation depth
) -> BtcFactId
```

### 3.2 Input Parameters

| Parameter | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| headers | bytes[] | 2 ≤ len ≤ 2016, each 80 bytes | Bitcoin block headers |
| tx_hash | bytes32 | Non-zero | Transaction hash to verify |
| merkle_branch | MerkleBranch | depth ≤ 14 | Merkle inclusion proof |
| block_index | uint16 | 0 ≤ block_index ≤ len(headers)-1 | Block containing tx |
| min_depth | uint16 | 1 ≤ min_depth ≤ 2016 | Required confirmations |

### 3.3 MerkleBranch Structure

```
MerkleBranch {
    siblings:  bytes32[]  // Sibling hashes at each level
    positions: uint8[]    // 0=left, 1=right at each level
}
```

### 3.4 Return Value

On success, returns a `BtcFactId` — a unique identifier for the recorded fact.

```
BtcFactId {
    account:   Address   // Account that verified
    height:    uint64    // Momentum height at verification
    index:     uint32    // Index within account's facts
}
```

### 3.5 Errors

| Error Code | Name | Description |
|------------|------|-------------|
| 1 | ERR_INSUFFICIENT_PLASMA | Account lacks resources |
| 2 | ERR_INVALID_HEADER_COUNT | Too few or too many headers |
| 3 | ERR_INVALID_HEADER_SIZE | Header not 80 bytes |
| 4 | ERR_POW_INVALID | Header hash exceeds target |
| 5 | ERR_CHAIN_BROKEN | Previous block hash mismatch |
| 6 | ERR_MERKLE_MISMATCH | Reconstructed root doesn't match |
| 7 | ERR_BRANCH_TOO_DEEP | Merkle branch exceeds 14 levels |
| 8 | ERR_INSUFFICIENT_DEPTH | Not enough confirmations |
| 9 | ERR_INVALID_BLOCK_INDEX | Block index out of range |

---

## 4. Plasma Cost Model

### 4.1 Cost Formula

The Plasma cost for verification is:

$$
C(\pi) = C_{\text{base}} + C_{\text{header}} \cdot h + C_{\text{merkle}} \cdot k
$$

where:
- $h$ = number of headers
- $k$ = Merkle branch depth
- $C_{\text{base}}$ = base transaction cost
- $C_{\text{header}}$ = cost per header verification
- $C_{\text{merkle}}$ = cost per Merkle level

### 4.2 Recommended Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| $C_{\text{base}}$ | 21,000 | Standard transaction base |
| $C_{\text{header}}$ | 5,000 | ~2 SHA256 + comparison |
| $C_{\text{merkle}}$ | 3,000 | ~2 SHA256 per level |

### 4.3 Cost Examples

| Proof Size | Headers | Merkle Depth | Total Plasma |
|------------|---------|--------------|--------------|
| Minimum (z=1) | 2 | 1 | 34,000 |
| Typical (z=6) | 7 | 10 | 86,000 |
| Large (z=100) | 101 | 14 | 568,000 |
| Maximum | 2016 | 14 | 10,143,000 |

### 4.4 Cost Bound

Maximum verification cost:

$$
C_{\text{max}} = C_{\text{base}} + C_{\text{header}} \cdot 2016 + C_{\text{merkle}} \cdot 14 = 10,143,000
$$

Accounts must have sufficient Plasma before invocation.

---

## 5. Account-Chain Semantics

### 5.1 Transaction Format

The ACI invocation is encoded as an account-block:

```
AccountBlock {
    type:        ACI_CALL
    aci_id:      "btc.spv.verify"
    data:        encoded(headers, tx_hash, merkle_branch, block_index, min_depth)
    plasma_used: C(π)
}
```

### 5.2 State Update

On successful verification:

1. A `BtcFact` is appended to the account's fact list
2. Plasma is consumed from the account
3. The fact is referenced in the account-block's `data` field
4. The account-block is included in the next Momentum

### 5.3 Momentum Behavior

**Critical**: Momentum producers do NOT re-verify SPV proofs.

The Momentum includes:
- Reference to the account-block
- State delta (ChangesHash) including the new fact
- No proof data (proofs are discarded after local verification)

This ensures global consensus cost is O(1) per fact, not O(proof size).

### 5.4 Fact Visibility

Verified facts are:
- Visible to the verifying account immediately
- Visible to other accounts after Momentum confirmation
- Queryable via account state reads
- Exportable in state proof bundles

---

## 6. BtcFact Structure

### 6.1 Stored Fact

```
BtcFact {
    tx_hash:       bytes32   // Bitcoin transaction hash
    block_hash:    bytes32   // Bitcoin block containing tx
    block_height:  uint32    // Bitcoin block height (if known)
    depth:         uint16    // Confirmation depth at verification
    verified_at:   uint64    // Zenon Momentum height
    chain_tip:     bytes32   // Bitcoin tip at verification
}
```

### 6.2 Fact Guarantees

A stored `BtcFact` asserts:

> "At Zenon Momentum height `verified_at`, the account owner presented a valid SPV proof showing Bitcoin transaction `tx_hash` was included in block `block_hash` with at least `depth` confirmations."

### 6.3 What Facts Do NOT Guarantee

- Current confirmation depth (may have increased)
- Transaction finality (reorgs possible but unlikely)
- Transaction validity (only inclusion, not semantics)
- Current Bitcoin chain state

---

## 7. Query Interface

### 7.1 Lookup by Transaction

```
GetBtcFact(account: Address, tx_hash: bytes32) -> BtcFact?
```

Returns the fact for a specific transaction, or null if not verified.

### 7.2 List Account Facts

```
ListBtcFacts(account: Address, offset: uint32, limit: uint32) -> BtcFact[]
```

Returns paginated list of facts verified by an account.

### 7.3 Check Fact Existence

```
HasBtcFact(account: Address, tx_hash: bytes32, min_depth: uint16) -> bool
```

Returns true if account has verified the transaction with at least `min_depth`.

---

## 8. Integration with State Proof Bundles

### 8.1 Bundle Inclusion

BtcFacts can be included in state proof bundles for cross-account verification:

```
StateProofBundle {
    account_block: AccountBlock
    btc_facts:     BtcFact[]      // Facts created by this block
    momentum_ref:  MomentumRef    // Anchor point
}
```

### 8.2 Light Client Verification

Light clients can verify BtcFacts by:

1. Obtaining the state proof bundle
2. Verifying the Momentum reference
3. Checking the account-block inclusion
4. Reading the fact from the bundle

Light clients do NOT need to re-verify the original SPV proof.

---

## 9. Security Considerations

### 9.1 Account Responsibility

The verifying account is responsible for:
- Providing valid proof data
- Selecting appropriate confirmation depth
- Understanding the security assumptions

### 9.2 Trust Model

Other accounts trusting a BtcFact are trusting:
- The verifying account's judgment
- The correctness of the SPV verification code
- Bitcoin's security (honest majority, PoW)

### 9.3 Fact Immutability

Once recorded, facts cannot be:
- Modified
- Deleted
- Backdated

This provides auditability but means invalid facts persist (though marked as such if challenged in Phase 3).

---

## 10. Implementation Notes

### 10.1 Verification Order

1. Check Plasma availability
2. Validate structural constraints
3. Verify all headers (PoW, linkage)
4. Verify Merkle inclusion
5. Check confirmation depth
6. Create and store fact
7. Consume Plasma

### 10.2 Atomicity

The entire operation is atomic:
- Either all checks pass and fact is created
- Or operation fails and no state changes

### 10.3 Replay Protection

Each verification creates a unique fact. Re-submitting the same proof:
- Succeeds (creates duplicate fact)
- Consumes Plasma again
- May be useful for "refreshing" confirmation depth

---

## 11. Example Usage

### 11.1 Verify a Payment

```
// Verify Bitcoin payment with 6 confirmations
result = VerifyBitcoinSPV(
    headers:       [H_0, H_1, H_2, H_3, H_4, H_5, H_6],
    tx_hash:       0x1234...,
    merkle_branch: MerkleBranch(siblings: [...], positions: [...]),
    block_index:   0,
    min_depth:     6
)

// Result: BtcFactId(account: z1..., height: 12345, index: 0)
```

### 11.2 Query Verified Fact

```
fact = GetBtcFact(my_account, 0x1234...)

// fact.tx_hash:      0x1234...
// fact.block_hash:   0xabcd...
// fact.depth:        6
// fact.verified_at:  12345
```

---

## 12. Future Extensions

### 12.1 Batch Verification

Verify multiple transactions in a single call (sharing headers).

### 12.2 Depth Refresh

Update an existing fact with additional confirmations without full re-verification.

### 12.3 Cross-Account Delegation

Allow accounts to delegate verification authority.

---

## 13. References

- [Bitcoin SPV Verifier Specification](../phase-0-foundation/bitcoin-spv-verifier-spec.md)
- [State Proof Bundles](/docs/notes/state-proof-bundles.md)
- [Taxonomy: Deterministic Fact Acceptance](/docs/research/taxonomy-deterministic-fact-acceptance.md)
- [Dynamic Plasma](/docs/notes/dynamic-plasma.md)
