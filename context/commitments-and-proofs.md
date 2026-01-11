# Commitments & Proofs

**Status:** Proposed (audit map for what is provable)

This document enumerates what a verifier can prove from existing commitments and what new commitments would be required for compact proofs.

## Definitions (informal)

- **Commitment:** an on-chain hash/signature value that binds some data.
- **Proof:** a data package that a verifier checks against commitments.
- **Decomposable commitment:** supports partial inclusion proofs (e.g., Merkle root).

## Proof taxonomy

### Header proof
Proves the existence/validity of a Momentum header in the canonical chain:
- signature verification
- hash linkage
- fork-choice
- producer eligibility (requires committee proof strategy)

### Inclusion proof (bounded list)
Proves a specific item is included in a bounded list committed by the header:
- can be “include the full list” if bounded (no Merkle needed)
- or Merkle-inclusion if a root exists

### State delta proof
Proves a state change occurred as part of a committed delta:
- easy if the commitment is decomposable (Merkle/vector)
- hard if commitment is a flat hash over an opaque dump

## Claims vs required commitments (table)

| Claim | Required on-chain commitment | Exists today? | Upgrade needed |
|---|---|---:|---|
| Verify Momentum continuity | header hash-link + signature | Yes | None |
| Verify producer signed header | producer public key set | Partial | committee proof scheme |
| Verify account-block header list for a Momentum | bounded header list or commitment | Partial | formal bound + canonical encoding |
| Verify full state patch for a Momentum | ChangesHash = H(full patch) | Yes (if defined) | None |
| Verify partial state delta (per-account slice) | decomposable delta commitment | No | Merkle/vector commitment |
| Verify committee membership at height H | committee commitment per epoch/height | No/Partial | committee root + proofs |
| Anchor auxiliary proofs (future) | header Data field / extra commitment slot | Reserved | consensus rule to enable |

## Minimal credible strategy

**MVP (verifiable today-ish):**
- headers + signatures + bounded lists + full-patch verification (slow path)

**Phase 2 (requires upgrades):**
- decomposable delta commitments
- committee root commitments
- structured proof bundles

## Design rules

1. Any third-party “bundle server” is untrusted.
2. Every bundle MUST be checkable against a canonical on-chain commitment.
3. If a claim cannot be checked, it MUST be labeled **Speculative**.
