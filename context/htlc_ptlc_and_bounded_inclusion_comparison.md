# HTLCs, PTLCs, and Bounded Inclusion

Research Note — Intuition Building

This note is informal and intended to build intuition. It does not introduce new protocol behavior. It clarifies how familiar primitives like HTLCs and PTLCs relate to the bounded inclusion model discussed in this repository.

---

## The Short Version

HTLCs and PTLCs are narrow, purpose-built instances of the same underlying idea that bounded inclusion generalizes:

> Accept a state transition if—and only if—a small, verifiable condition is satisfied, without re-executing global state.

They do not require global transaction replay, full ledger knowledge, or general-purpose execution.

---

## What HTLCs / PTLCs Actually Do

An HTLC or PTLC enforces a condition of the form:

> "This output is spendable if a specific cryptographic predicate is satisfied."

**Examples:**

- HTLC: reveal a preimage before a timeout
- PTLC: satisfy a discrete-log–based condition

**Crucially:**

- The verifier does not re-execute prior transactions
- The verifier does not care about transaction ordering beyond the referenced output
- The verifier checks only a small proof against a committed state

This is already bounded verification.

---

## What Bounded Inclusion Generalizes

Bounded inclusion takes the same verification pattern and removes the hard-coded use case.

**Instead of:**

- "Is this hash preimage valid?"
- "Does this signature satisfy this script?"

**It asks:**

- "Is this local state consistent with a header-committed state root?"

**Formally:**

- HTLCs/PTLCs verify one specific state predicate
- Bounded inclusion verifies arbitrary local state predicates, as long as they are committed in the state root

**Both:**

- Avoid global execution
- Rely on cryptographic commitments
- Trade completeness for verifiability under tight resource bounds

---

## Why This Distinction Matters

HTLCs and PTLCs are usually viewed as features or contracts.

Bounded inclusion is a verification primitive.

**That means:**

- HTLCs/PTLCs can be seen as special cases inside the bounded inclusion envelope
- Bounded inclusion is not proposing new trust assumptions
- It is naming and formalizing a pattern already used successfully in limited contexts

---

## What Bounded Inclusion Does Not Claim

This model does not claim:

- Full transaction traceability
- Canonical chain detection
- Global consensus safety
- Censorship resistance

Those limits are explicit and intentional.

HTLCs/PTLCs succeed precisely because they operate within similar constraints.

---

## Summary

If HTLCs and PTLCs are acceptable, safe, and useful primitives, then bounded inclusion should be understood as:

> The same idea, made explicit, generalized, and applicable to browser-scale verification of local state.

Nothing more—and nothing less.
