# Bitcoin SPV Fraud Proof Specification

**Phase**: 3 — Optimistic Checkpointing
**Status**: Exploratory / Research Draft

---

## 1. Overview

This specification defines fraud proofs for challenging invalid Bitcoin SPV checkpoints. Fraud proofs enable any network participant to prove that a submitted checkpoint is incorrect, triggering its invalidation and the slashing of the submitter's bond.

---

## 2. Fraud Proof Types

### 2.1 Summary

| Type | Proves | Evidence Required |
|------|--------|-------------------|
| HIGHER_WORK | Submitted chain is not canonical | Competing header chain with more work |
| INVALID_POW | Header fails proof-of-work | The failing header |
| BROKEN_CHAIN | Headers don't link properly | The non-linking headers |
| MERKLE_INVALID | Transaction not in claimed block | Correct Merkle computation |
| DEPTH_FALSE | Confirmation depth overstated | Current chain showing fewer confirmations |

---

## 3. HIGHER_WORK Fraud Proof

### 3.1 Purpose

Proves that the checkpoint's header chain is not the canonical Bitcoin chain (not the chain with maximum cumulative work).

### 3.2 Structure

```
HigherWorkProof {
    checkpoint_id:     u64           // Challenged checkpoint
    competing_chain:   bytes[]       // Headers of higher-work chain
    fork_height:       u32           // Height where chains diverge
}
```

### 3.3 Verification Algorithm

```
VerifyHigherWorkProof(proof, checkpoint):
    # Get checkpoint's chain tip and work
    submitted_tip = checkpoint.chain_tip
    submitted_work = checkpoint.chain_work

    # Validate competing chain
    if not ValidateHeaderChain(proof.competing_chain):
        return INVALID_CHALLENGE

    # Compute competing chainwork
    competing_work = ComputeChainwork(proof.competing_chain)

    # Check fork point
    if not ChainsShareAncestor(
        checkpoint.proof_data.headers,
        proof.competing_chain,
        proof.fork_height
    ):
        return INVALID_CHALLENGE

    # Compare work
    if competing_work > submitted_work:
        return FRAUD_PROVEN
    else:
        return INVALID_CHALLENGE
```

### 3.4 Requirements

- Competing chain must be valid (PoW, linkage)
- Chains must share common ancestor at fork_height
- Competing chainwork must exceed submitted chainwork

---

## 4. INVALID_POW Fraud Proof

### 4.1 Purpose

Proves that one or more headers in the checkpoint's chain have invalid proof-of-work.

### 4.2 Structure

```
InvalidPowProof {
    checkpoint_id:   u64      // Challenged checkpoint
    header_index:    u16      // Index of invalid header
}
```

### 4.3 Verification Algorithm

```
VerifyInvalidPowProof(proof, checkpoint):
    # Get the header in question
    headers = checkpoint.proof_data.headers
    if proof.header_index >= len(headers):
        return INVALID_CHALLENGE

    header = headers[proof.header_index]

    # Compute hash and target
    block_hash = SHA256(SHA256(header))
    target = DecodeTarget(header.bits)

    # Check PoW
    if block_hash > target:
        return FRAUD_PROVEN
    else:
        return INVALID_CHALLENGE
```

### 4.4 Note

This should normally not occur if submitters run proper verification. It catches implementation bugs or malicious submissions.

---

## 5. BROKEN_CHAIN Fraud Proof

### 5.1 Purpose

Proves that the header chain has broken linkage (prev_block doesn't match).

### 5.2 Structure

```
BrokenChainProof {
    checkpoint_id:   u64      // Challenged checkpoint
    break_index:     u16      // Index where chain breaks
}
```

### 5.3 Verification Algorithm

```
VerifyBrokenChainProof(proof, checkpoint):
    headers = checkpoint.proof_data.headers

    if proof.break_index == 0 or proof.break_index >= len(headers):
        return INVALID_CHALLENGE

    # Get adjacent headers
    prev_header = headers[proof.break_index - 1]
    curr_header = headers[proof.break_index]

    # Compute expected prev_block
    expected_prev = SHA256(SHA256(prev_header))

    # Check linkage
    if curr_header.prev_block != expected_prev:
        return FRAUD_PROVEN
    else:
        return INVALID_CHALLENGE
```

---

## 6. MERKLE_INVALID Fraud Proof

### 6.1 Purpose

Proves that the Merkle inclusion proof is invalid — the transaction is not actually in the claimed block.

### 6.2 Structure

```
MerkleInvalidProof {
    checkpoint_id:    u64           // Challenged checkpoint
    correct_branch:   MerkleBranch  // Optional: correct branch proving different root
}
```

### 6.3 Verification Algorithm

```
VerifyMerkleInvalidProof(proof, checkpoint):
    # Reconstruct Merkle root from submitted proof
    submitted_root = MerkleReconstruct(
        checkpoint.tx_hash,
        checkpoint.proof_data.merkle_branch
    )

    # Get actual Merkle root from header
    block_header = checkpoint.proof_data.headers[checkpoint.proof_data.block_index]
    actual_root = block_header.merkle_root

    # Check match
    if submitted_root != actual_root:
        return FRAUD_PROVEN
    else:
        return INVALID_CHALLENGE
```

### 6.4 Alternative: Prove Different Transaction

A challenger might provide evidence that a different transaction occupies the claimed position:

```
MerkleConflictProof {
    checkpoint_id:     u64
    conflicting_tx:    bytes32       // Different tx at same position
    conflicting_branch: MerkleBranch // Branch proving conflicting tx
}
```

---

## 7. DEPTH_FALSE Fraud Proof

### 7.1 Purpose

Proves that the claimed confirmation depth was false at submission time.

### 7.2 Complexity

This is the most complex fraud proof because it requires proving state at a past point in time.

### 7.3 Structure

```
DepthFalseProof {
    checkpoint_id:       u64
    actual_chain:        bytes[]     // Chain at submission time
    submission_tip:      bytes32     // Actual tip at submission
}
```

### 7.4 Verification Approach

**Option A: Timestamp-based**
- Use Bitcoin block timestamps to establish submission-time state
- Limited precision due to timestamp manipulation

**Option B: Zenon-anchored**
- Zenon Momentum commits to observed Bitcoin tip
- Challenge proves different tip was valid at that Momentum

**Option C: Retroactive Chainwork**
- Prove that at submission time, a different chain had more work
- Requires historical data

### 7.5 Practical Considerations

Depth false proofs are difficult to construct and verify. Consider:
- Only accepting challenges within short window
- Requiring significant evidence
- Higher challenger bond for this type

---

## 8. Challenge Submission

### 8.1 Interface

```
SubmitFraudProof(
    checkpoint_id:   u64,
    proof_type:      FraudProofType,
    proof_data:      bytes,
    challenger_bond: u64
) -> ChallengeResult
```

### 8.2 Validation Steps

1. Checkpoint exists and is PENDING
2. Challenge window not expired
3. Challenger has sufficient bond
4. Proof type is valid
5. Proof data is well-formed

### 8.3 Resolution

```
enum ChallengeResult {
    FRAUD_PROVEN,       // Checkpoint invalidated, submitter slashed
    INVALID_CHALLENGE,  // Challenge rejected, challenger slashed
    PENDING,            // Complex challenge requires further processing
}
```

---

## 9. Adjudication Process

### 9.1 Immediate Resolution

For simple fraud proofs (INVALID_POW, BROKEN_CHAIN, MERKLE_INVALID):
- Verification is deterministic
- Resolution in same Momentum
- No dispute possible

### 9.2 Complex Resolution

For HIGHER_WORK and DEPTH_FALSE:
- May require multi-step verification
- Could involve interactive protocol
- Longer resolution time

### 9.3 Adjudication Algorithm

```
Adjudicate(challenge):
    match challenge.proof_type:
        HIGHER_WORK:
            result = VerifyHigherWorkProof(challenge.proof, challenge.checkpoint)

        INVALID_POW:
            result = VerifyInvalidPowProof(challenge.proof, challenge.checkpoint)

        BROKEN_CHAIN:
            result = VerifyBrokenChainProof(challenge.proof, challenge.checkpoint)

        MERKLE_INVALID:
            result = VerifyMerkleInvalidProof(challenge.proof, challenge.checkpoint)

        DEPTH_FALSE:
            result = VerifyDepthFalseProof(challenge.proof, challenge.checkpoint)

    ApplyResult(result, challenge)
```

---

## 10. Consequences

### 10.1 Fraud Proven

When fraud is proven:

```
1. Checkpoint status -> INVALIDATED
2. Submitter bond slashed:
   - Challenger receives α × bond
   - Protocol receives (1-α) × bond
3. Challenger bond returned
4. Event: CheckpointInvalidated(checkpoint_id, challenger)
```

### 10.2 Invalid Challenge

When challenge is rejected:

```
1. Checkpoint remains PENDING
2. Challenger bond slashed:
   - Submitter receives α × challenger_bond
   - Protocol receives (1-α) × challenger_bond
3. Event: ChallengeRejected(challenge_id)
```

### 10.3 Slashing Parameters

| Parameter | Symbol | Suggested Value |
|-----------|--------|-----------------|
| Challenger reward ratio | α | 0.5 |
| Minimum submitter bond | $B_{min}$ | 100 ZNN |
| Minimum challenger bond | $C_{min}$ | 10 ZNN |

---

## 11. Edge Cases

### 11.1 Multiple Challenges

If multiple challenges are submitted:
- Process in submission order
- First valid challenge wins
- Subsequent challenges refunded (no double-slashing)

### 11.2 Challenge During Finalization

If challenge arrives as finalization is processing:
- Challenge takes priority
- Finalization delayed pending resolution

### 11.3 Invalid Challenge to Valid Checkpoint

Submitter should not be penalized for defending against invalid challenges:
- Only challenger loses bond
- Submitter receives portion of challenger bond

### 11.4 Reorg During Challenge Window

If Bitcoin reorgs during challenge window:
- HIGHER_WORK challenges become easier to construct
- Checkpoints with now-invalid depth may be challenged
- Consider extending window during detected reorgs

---

## 12. Security Considerations

### 12.1 Griefing Attacks

**Attack**: Submit valid checkpoint, spam invalid challenges.

**Defense**:
- Challenger bond required
- Invalid challenges punished
- Submitter compensated from challenger bond

### 12.2 Challenge Withholding

**Attack**: Know of fraud but wait until window nearly expires.

**Impact**: Minimal — fraud still detected within window.

**Consideration**: No incentive to delay if challenge will succeed.

### 12.3 Proof Availability

**Issue**: Checkpoint proof data needed for verification.

**Defense**:
- Proof stored on submission
- Available throughout challenge window
- Challengers can request proof data

---

## 13. Gas/Plasma Costs

### 13.1 Cost Estimates

| Operation | Estimated Cost |
|-----------|----------------|
| Submit challenge | 50,000 Plasma |
| Verify INVALID_POW | 10,000 Plasma |
| Verify BROKEN_CHAIN | 10,000 Plasma |
| Verify MERKLE_INVALID | 20,000 Plasma |
| Verify HIGHER_WORK | 100,000+ Plasma |
| Verify DEPTH_FALSE | 150,000+ Plasma |

### 13.2 Cost Recovery

- Winning party's costs recovered from loser's bond
- Protocol may subsidize verification costs

---

## 14. Implementation Notes

### 14.1 Proof Data Encoding

All proofs should use canonical encoding:
- Deterministic serialization
- No ambiguity in interpretation
- Version field for upgrades

### 14.2 Verification Determinism

All verification must be:
- Deterministic across implementations
- Reproducible given same inputs
- No external dependencies during verification

### 14.3 Testing

Comprehensive test vectors needed:
- Valid fraud proofs (should succeed)
- Invalid fraud proofs (should fail)
- Edge cases (boundary conditions)

---

## 15. Open Questions

1. **Interactive proofs**: Should complex challenges use interactive verification?

2. **Challenge bonds**: Should challenger bond scale with checkpoint bond?

3. **Time limits**: How long for complex challenge resolution?

4. **Proof compression**: Can fraud proofs be made more compact?

5. **Cross-chain generalization**: How to adapt for other chains?

---

## 16. References

- [Optimistic Bitcoin Fact Checkpointing](optimistic-btc-checkpointing.md)
- [Bitcoin SPV Verifier Specification](../phase-0-foundation/bitcoin-spv-verifier-spec.md)
- [Bitcoin SPV Threat Model](../phase-0-foundation/bitcoin-spv-threat-model.md)
