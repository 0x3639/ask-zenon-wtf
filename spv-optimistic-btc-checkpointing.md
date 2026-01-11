# Optimistic Bitcoin Fact Checkpointing

**Phase**: 3 — Optimistic Checkpointing
**Status**: Exploratory / Research Draft

---

## 1. Overview

This specification defines a mechanism for promoting locally verified Bitcoin facts to globally visible checkpoints. The optimistic approach accepts facts provisionally, with a challenge window during which fraud proofs can invalidate incorrect submissions.

**Key Properties**:
- Global visibility without global verification cost
- Fraud proofs enable anyone to challenge invalid facts
- Challenge window provides security against false submissions
- Submitters stake bonds as economic security

---

## 2. Design Rationale

### 2.1 Problem Statement

Phase 1 creates locally verified Bitcoin facts in individual account states. These facts are:
- Visible only to accounts that query the verifying account
- Not part of global consensus
- Not challengeable by other parties

For cross-chain applications, we need facts that are:
- Globally visible and queryable
- Validated by the network (not just one account)
- Resistant to false submissions

### 2.2 Solution: Optimistic Checkpointing

Instead of requiring every node to verify every proof:

1. Submitter verifies locally and posts fact + bond
2. Network accepts fact provisionally
3. Challenge window allows fraud proof submission
4. After window closes, fact becomes canonical

This amortizes verification cost: only challenged facts require network-wide verification.

---

## 3. Checkpoint Structure

### 3.1 BTC_FACT Checkpoint

```
BtcCheckpoint {
    // Identification
    checkpoint_id:   u64         // Sequential global ID

    // Bitcoin data
    tx_hash:         bytes32     // Bitcoin transaction hash
    block_hash:      bytes32     // Containing block
    block_height:    u32         // Block height
    depth:           u16         // Confirmations at submission
    merkle_root:     bytes32     // Block's Merkle root
    chain_tip:       bytes32     // Bitcoin tip at submission
    chain_work:      bytes32     // Cumulative chainwork

    // Submission context
    submitter:       Address     // Account that submitted
    bond:            u64         // Staked bond amount
    submitted_at:    u64         // Momentum height of submission

    // Status
    status:          CheckpointStatus
    finalized_at:    u64         // Momentum height when finalized (0 if pending)
}
```

### 3.2 Checkpoint Status

```
enum CheckpointStatus {
    PENDING,      // Within challenge window
    CHALLENGED,   // Under active challenge
    FINALIZED,    // Challenge window passed, accepted
    INVALIDATED   // Fraud proof accepted, rejected
}
```

---

## 4. Submission Workflow

### 4.1 Prerequisites

Before submitting a checkpoint, the account must:
1. Have a verified local BtcFact (Phase 1)
2. Hold sufficient bond in the checkpoint contract
3. Meet any rate-limiting requirements

### 4.2 Submission Process

```
SubmitBtcCheckpoint(
    local_fact_id:  u32,       // Reference to local BtcFact
    proof:          SpvProof,  // Full proof data for challenge verification
    bond_amount:    u64        // Bond to stake
) -> CheckpointId
```

**Steps**:
1. Validate local fact exists and is recent
2. Lock bond from submitter's account
3. Create pending checkpoint
4. Store proof data for potential challenges
5. Start challenge window timer
6. Emit `CheckpointSubmitted` event

### 4.3 Proof Storage

During the challenge window, the full SPV proof must be available:

```
CheckpointProofData {
    checkpoint_id:  u64
    headers:        bytes[]     // Full header chain
    merkle_branch:  MerkleBranch
    block_index:    u16
    stored_until:   u64         // Momentum height to retain
}
```

Proof data can be pruned after finalization (unless needed for historical reference).

---

## 5. Challenge Window

### 5.1 Window Parameters

| Parameter | Symbol | Suggested Value | Rationale |
|-----------|--------|-----------------|-----------|
| Window duration | $T$ | 1000 Momentums (~16 hours) | Balance security and latency |
| Minimum bond | $B_{min}$ | 100 ZNN | Economic barrier to spam |
| Challenge bond | $C_{min}$ | 10 ZNN | Lower barrier for challenges |

### 5.2 Window States

```
Time: 0 ──────────────────────── T ───────────────────
      │                          │
      │      Challenge Window    │    Finalized
      │                          │
      ├─ PENDING ───────────────►├─ FINALIZED
      │                          │
      │    (if challenged)       │    (if fraud proven)
      └─────── CHALLENGED ───────┴─── INVALIDATED
```

### 5.3 During the Window

While PENDING:
- Checkpoint is visible but not final
- Anyone can submit a challenge
- Submitter cannot withdraw bond
- Proof data must remain available

---

## 6. Finalization

### 6.1 Automatic Finalization

If no valid challenge is submitted before window closes:

```
FinalizeCheckpoint(checkpoint_id) -> bool
```

**Steps**:
1. Verify window has elapsed
2. Verify no active challenges
3. Update status to FINALIZED
4. Return bond to submitter
5. Emit `CheckpointFinalized` event

### 6.2 Finalization Trigger

Finalization can be triggered by:
- Anyone (permissionless call)
- Automated process after window
- Submitter claiming their bond

### 6.3 Post-Finalization

Finalized checkpoints are:
- Globally queryable
- Immutable
- Usable as trust anchors for other protocols

---

## 7. Challenge Mechanism

### 7.1 Challenge Submission

```
ChallengeCheckpoint(
    checkpoint_id:  u64,
    challenge_type: ChallengeType,
    evidence:       bytes        // Type-specific evidence
) -> ChallengeId
```

### 7.2 Challenge Types

| Type | Evidence Required | Description |
|------|-------------------|-------------|
| HIGHER_WORK | Competing header chain | Submitter's chain not canonical |
| INVALID_POW | Header with invalid PoW | Header fails PoW check |
| BROKEN_CHAIN | Non-linking headers | Chain linkage failure |
| MERKLE_INVALID | Merkle recomputation | Transaction not in block |
| DEPTH_FALSE | Updated chain showing fewer confirmations | Depth was overstated |

### 7.3 Challenge Resolution

See [Bitcoin SPV Fraud Proofs](bitcoin-spv-fraud-proofs.md) for detailed challenge resolution.

---

## 8. Bond Economics

### 8.1 Submitter Bond

| Scenario | Bond Outcome |
|----------|--------------|
| Finalized (no challenge) | Returned to submitter |
| Invalid challenge | Returned to submitter |
| Valid challenge | Slashed |

### 8.2 Challenger Bond

| Scenario | Bond Outcome |
|----------|--------------|
| Challenge upheld | Returned + reward from submitter's bond |
| Challenge rejected | Slashed |

### 8.3 Slashing Distribution

When submitter is slashed:
- Challenger receives reward portion
- Protocol receives remainder (burn or treasury)

```
Slashing:
  Challenger reward: α × submitter_bond  (e.g., α = 0.5)
  Protocol:          (1-α) × submitter_bond
```

---

## 9. Integration with Momentum

### 9.1 Momentum Data Field

Checkpoints are stored in Momentum via dedicated data field:

```
MomentumData {
    // ... existing fields ...
    btc_checkpoints: CheckpointDelta[]
}

CheckpointDelta {
    action:     CREATE | FINALIZE | INVALIDATE
    checkpoint: BtcCheckpoint
}
```

### 9.2 Checkpoint Ordering

Within a Momentum:
1. New submissions processed first
2. Finalizations processed second
3. Challenges/invalidations processed third

### 9.3 Cross-Momentum References

Checkpoints can be referenced by ID from any Momentum after creation:

```
GetBtcCheckpoint(checkpoint_id) -> BtcCheckpoint?
```

---

## 10. Query Interface

### 10.1 Checkpoint Queries

```
// By ID
GetBtcCheckpoint(checkpoint_id: u64) -> BtcCheckpoint?

// By transaction hash
GetBtcCheckpointByTx(tx_hash: bytes32) -> BtcCheckpoint?

// List by status
ListBtcCheckpoints(status: CheckpointStatus, limit: u32) -> BtcCheckpoint[]

// List by submitter
ListBtcCheckpointsBySubmitter(address: Address) -> BtcCheckpoint[]
```

### 10.2 Status Queries

```
// Check if transaction has finalized checkpoint
HasFinalizedCheckpoint(tx_hash: bytes32, min_depth: u16) -> bool

// Get checkpoint status
GetCheckpointStatus(checkpoint_id: u64) -> CheckpointStatus
```

---

## 11. Security Analysis

### 11.1 Attack: Submit False Checkpoint

**Attack**: Submit checkpoint for non-existent Bitcoin transaction.

**Defense**:
- Challenger can provide proof of non-inclusion or different chain
- Submitter loses bond

**Cost to attacker**: Bond + reputation

### 11.2 Attack: Grief Challenger

**Attack**: Submit valid checkpoint, then challenge it to waste challenger's bond.

**Defense**:
- Challenger must provide valid fraud proof
- Invalid challenges are rejected and bond slashed

### 11.3 Attack: Eclipse + False Submission

**Attack**: Eclipse victim, submit false checkpoint, hope no one challenges.

**Defense**:
- Challenge window long enough for honest parties to respond
- Multiple network participants monitor checkpoints

### 11.4 Attack: Challenge Spam

**Attack**: Submit many invalid challenges to delay finalization.

**Defense**:
- Challenge bond required
- Invalid challenges slashed
- Parallel challenge processing

---

## 12. Example Workflows

### 12.1 Happy Path

```
1. Alice verifies BTC payment locally (Phase 1)
2. Alice submits checkpoint with 100 ZNN bond
3. Challenge window opens (1000 Momentums)
4. No challenges submitted
5. Window closes
6. Anyone calls FinalizeCheckpoint()
7. Alice receives 100 ZNN back
8. Checkpoint is FINALIZED
```

### 12.2 Successful Challenge

```
1. Mallory submits false checkpoint
2. Bob notices the Bitcoin chain shows different data
3. Bob submits HIGHER_WORK challenge with competing chain
4. Challenge is evaluated:
   - Bob's chain has more work
   - Mallory's checkpoint invalid
5. Mallory's bond slashed:
   - Bob receives 50 ZNN
   - Protocol receives 50 ZNN
6. Checkpoint status: INVALIDATED
```

---

## 13. Open Questions

### 13.1 Window Duration

- What is the optimal challenge window duration?
- Should it scale with checkpoint value or depth?
- How to handle network partitions during window?

### 13.2 Bond Sizing

- Should bond scale with claimed confirmation depth?
- How to set bond to balance security and accessibility?
- Should there be a bond market?

### 13.3 Proof Availability

- Who is responsible for proof storage during window?
- Should proofs be stored on-chain or off-chain?
- How to handle proof unavailability during challenge?

### 13.4 Upgrade Path

- How to upgrade checkpoint format?
- Migration strategy for pending checkpoints?
- Versioning scheme?

---

## 14. Future Extensions

### 14.1 Batch Checkpoints

Submit multiple related transactions in one checkpoint:
- Share header chain across transactions
- Reduced per-transaction cost
- Atomic acceptance/rejection

### 14.2 Recursive Checkpoints

Reference existing finalized checkpoints:
- Build on previous verification
- Reduce redundant work
- Chain of trust

### 14.3 Cross-Chain Generalization

Extend pattern to other chains:
- Ethereum receipts
- Other PoW chains
- Eventually PoS chains with different fraud proofs

---

## 15. References

- [Bitcoin SPV Fraud Proofs](bitcoin-spv-fraud-proofs.md)
- [Bitcoin Fact Storage](../phase-1-account-integration/bitcoin-fact-storage.md)
- [VerifyBitcoinSPV ACI](../phase-1-account-integration/verify-bitcoin-spv-aci.md)
- [Bonded Relayer Model](../phase-4-incentives/bonded-relayer-model.md)
