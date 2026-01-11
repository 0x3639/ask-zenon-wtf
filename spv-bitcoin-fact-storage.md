# Account-Level Bitcoin Fact Storage

**Phase**: 1 — Account-Level Verification (Isolation)
**Status**: Exploratory / Research Draft

---

## 1. Overview

This document specifies how verified Bitcoin facts are stored, indexed, and accessed within Zenon's account-chain model. Facts created by the `VerifyBitcoinSPV` ACI persist in account state and serve as the foundation for cross-chain verification.

---

## 2. Storage Model

### 2.1 Account State Extension

Each account's state is extended with a Bitcoin facts store:

```
AccountState {
    // ... existing fields ...

    btc_facts:       BtcFact[]         // Ordered list of verified facts
    btc_fact_index:  Map<bytes32, u32> // tx_hash -> fact index
    btc_fact_count:  u32               // Total facts verified
}
```

### 2.2 BtcFact Structure

```
BtcFact {
    // Identification
    fact_id:       u32       // Sequential index within account
    tx_hash:       bytes32   // Bitcoin transaction hash

    // Bitcoin context
    block_hash:    bytes32   // Block containing the transaction
    merkle_root:   bytes32   // Block's Merkle root
    block_height:  u32       // Bitcoin block height (0 if unknown)

    // Verification context
    depth:         u16       // Confirmation depth at verification
    chain_tip:     bytes32   // Tip of submitted header chain
    chain_work:    bytes32   // Cumulative work of submitted chain

    // Zenon context
    verified_at:   u64       // Momentum height when verified
    block_ref:     bytes32   // Account-block hash containing verification
}
```

### 2.3 Size Estimates

| Field | Size (bytes) |
|-------|--------------|
| fact_id | 4 |
| tx_hash | 32 |
| block_hash | 32 |
| merkle_root | 32 |
| block_height | 4 |
| depth | 2 |
| chain_tip | 32 |
| chain_work | 32 |
| verified_at | 8 |
| block_ref | 32 |
| **Total** | **210 bytes** |

---

## 3. Indexing

### 3.1 Primary Index

Facts are stored in insertion order and accessed by sequential `fact_id`:

```
GetFactById(account, fact_id) -> BtcFact
```

### 3.2 Transaction Hash Index

A secondary index maps transaction hashes to fact IDs:

```
btc_fact_index[tx_hash] = fact_id
```

This enables O(1) lookup by transaction:

```
GetFactByTxHash(account, tx_hash) -> BtcFact
```

### 3.3 Index Constraints

- Each transaction hash maps to at most one fact per account
- Re-verifying the same transaction overwrites the index entry
- The old fact remains accessible by fact_id but is no longer the "current" fact for that tx_hash

---

## 4. Lifecycle

### 4.1 Fact Creation

```
1. Account invokes VerifyBitcoinSPV(proof)
2. Verification succeeds
3. New BtcFact created with:
   - fact_id = btc_fact_count
   - verified_at = current Momentum height
   - block_ref = current account-block hash
4. btc_fact_count incremented
5. btc_fact_index[tx_hash] = fact_id
6. Fact appended to btc_facts list
```

### 4.2 Fact Immutability

Once created, facts are immutable:
- No modification
- No deletion
- No retroactive changes

This ensures auditability and prevents historical manipulation.

### 4.3 Fact Refresh

To record additional confirmations:

1. Re-invoke `VerifyBitcoinSPV` with updated proof
2. New fact is created with higher `depth`
3. Index points to new fact
4. Old fact remains accessible by fact_id

---

## 5. Query Interface

### 5.1 Single Fact Queries

```
// By fact ID
GetBtcFact(account: Address, fact_id: u32) -> BtcFact?

// By transaction hash
GetBtcFactByTx(account: Address, tx_hash: bytes32) -> BtcFact?

// Check existence with minimum depth
HasBtcFact(account: Address, tx_hash: bytes32, min_depth: u16) -> bool
```

### 5.2 List Queries

```
// Paginated list
ListBtcFacts(account: Address, offset: u32, limit: u32) -> BtcFact[]

// Count
CountBtcFacts(account: Address) -> u32
```

### 5.3 Filter Queries

```
// Facts verified after a specific Momentum
ListBtcFactsSince(account: Address, momentum_height: u64) -> BtcFact[]

// Facts with minimum depth
ListBtcFactsWithDepth(account: Address, min_depth: u16) -> BtcFact[]
```

---

## 6. Cross-Account Visibility

### 6.1 Read Access

Any account can read another account's Bitcoin facts:

```
other_fact = GetBtcFact(other_account, tx_hash)
```

This is a read-only operation with no Plasma cost beyond standard state access.

### 6.2 Trust Considerations

When relying on another account's fact:

- You trust their verification was performed correctly
- You trust they used appropriate confirmation depth
- You trust the SPV verification code itself
- You inherit Bitcoin's security assumptions

### 6.3 Use Cases

Cross-account visibility enables:
- Decentralized oracles (multiple accounts verify same tx)
- Aggregated confidence (consensus among verifiers)
- Proof markets (specialized verifiers serve others)

---

## 7. Relationship to State Proof Bundles

### 7.1 Bundle Structure

Bitcoin facts are included in state proof bundles:

```
StateProofBundle {
    account_block:  AccountBlock      // Block that created/referenced facts
    state_delta:    StateDelta        // Changes including btc_facts updates
    btc_facts:      BtcFact[]         // Facts for this block (convenience)
    momentum_ref:   MomentumRef       // Anchor
}
```

### 7.2 Light Client Verification

Light clients verify fact existence by:

1. Obtaining state proof bundle
2. Verifying Momentum anchor
3. Checking account-block inclusion
4. Extracting fact from state delta

Light clients do NOT re-verify the original Bitcoin SPV proof.

### 7.3 Proof Serving

Sentries or Sentinels can serve:
- Fact existence proofs
- Fact content proofs
- Historical fact queries

---

## 8. Storage Considerations

### 8.1 Per-Account Limits

To prevent unbounded state growth, consider:

| Limit | Value | Rationale |
|-------|-------|-----------|
| Max facts per account | 10,000 | Practical limit |
| Max fact size | 210 bytes | Fixed structure |
| Max total storage | ~2 MB | Per-account bound |

### 8.2 Pruning Policy

Facts are permanent by default. Optional pruning strategies:

**Option A: No Pruning**
- All facts retained forever
- Simplest implementation
- Unbounded growth

**Option B: Age-Based Pruning**
- Facts older than N Momentums prunable
- Maintains recent history
- Reduces long-term storage

**Option C: Depth-Based Retention**
- Keep only highest-depth fact per tx_hash
- Reduces redundancy
- Loses verification history

### 8.3 Archive vs Active

Consider separating:
- **Active facts**: Recent, frequently accessed
- **Archive facts**: Old, rarely accessed, cheaper storage

---

## 9. Expiration Policy

### 9.1 Options

**Option 1: No Expiration**
- Facts never expire
- Always available for reference
- Highest storage cost

**Option 2: Fixed TTL**
- Facts expire after N Momentums
- Predictable lifecycle
- May lose needed facts

**Option 3: Renewal**
- Facts have TTL but can be renewed
- Account pays to extend
- Balances cost and availability

### 9.2 Recommendation

For initial implementation: **No Expiration**

Rationale:
- Simplest semantics
- Cross-chain references may need old facts
- Storage cost is bounded by account limits

Expiration can be added later if needed.

---

## 10. Consistency Guarantees

### 10.1 Within Account

Facts are:
- Ordered by fact_id
- Created atomically with verification
- Immediately visible to subsequent account operations

### 10.2 Across Accounts

Facts are visible to other accounts after:
- Account-block is included in Momentum
- Momentum is finalized

### 10.3 Temporal Ordering

```
fact_1.verified_at < fact_2.verified_at
    implies fact_1.fact_id < fact_2.fact_id
    (within same account)
```

---

## 11. Integration with Phase 3

### 11.1 Checkpoint Submission

In Phase 3, verified facts can be submitted for global checkpointing:

```
SubmitBtcCheckpoint(fact_id) -> CheckpointId
```

This references the local fact and makes it globally visible.

### 11.2 Fact Upgrades

Checkpointed facts gain:
- Global visibility (not just account state)
- Fraud proof protection
- Canonical status after challenge window

---

## 12. Example Workflows

### 12.1 Verify and Store

```
// Account verifies a Bitcoin payment
fact_id = VerifyBitcoinSPV(proof)

// Fact is now stored
fact = GetBtcFact(my_account, fact_id)
assert fact.tx_hash == expected_tx
assert fact.depth >= 6
```

### 12.2 Check Payment Before Action

```
// Before releasing goods, check payment fact
if HasBtcFact(buyer_account, payment_tx_hash, 6):
    release_goods()
else:
    wait_for_verification()
```

### 12.3 Query Historical Verifications

```
// List all facts I've verified
facts = ListBtcFacts(my_account, offset=0, limit=100)

for fact in facts:
    print(f"Verified {fact.tx_hash} at depth {fact.depth}")
```

---

## 13. Open Questions

1. **Optimal storage structure**: B-tree vs linear array for large fact counts?

2. **Cross-shard queries**: If accounts are sharded, how to query across shards?

3. **Bulk operations**: Should batch verification create multiple facts atomically?

4. **Fact references**: Can facts reference other facts (e.g., related transactions)?

5. **Garbage collection**: When is it safe to prune old facts?

---

## 14. References

- [VerifyBitcoinSPV ACI Specification](verify-bitcoin-spv-aci.md)
- [State Proof Bundles](/docs/notes/state-proof-bundles.md)
- [Optimistic Bitcoin Fact Checkpointing](../phase-3-optimistic-layer/optimistic-btc-checkpointing.md)
