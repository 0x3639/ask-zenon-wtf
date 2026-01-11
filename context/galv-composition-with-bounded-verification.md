Composing Genesis-Anchored Lineage with Bounded Verification

Status

Non-normative architectural note
This document describes how Genesis-Anchored Lineage Verification (GALV) composes with existing Zenon verification primitives.
It does not introduce new guarantees.

⸻

1. Purpose

Genesis-Anchored Lineage Verification (GALV) establishes a single, minimal property:

A verifier can cryptographically bind a chain’s origin and earliest state to an immutable external timestamp and trust root (Bitcoin), without relying on continuous connectivity or operator trust.

By design, GALV is intentionally narrow.
Its value emerges only when composed with other verification mechanisms.

This note explains how GALV integrates with:

	•	header-only verification
	•	bounded inclusion
	•	minimal state frontier verification

and why this composition is particularly relevant for edge and offline-resilient verifiers.

⸻

2. GALV as a Trust Root, Not a Verifier

GALV does not verify execution, data availability, or consensus correctness.

Instead, it provides:

	•	an unforgeable starting point
	•	a globally agreed lower bound on time
	•	a lineage anchor external to the system itself

Formally, GALV establishes:

Let

	•	G_Z be the Zenon genesis commitment
	•	B_h be a Bitcoin block header with height h
	•	A(G_Z, B_h) be a verifiable anchoring relation

Then any verifier can assert:

	1.	G_Z existed no earlier than Bitcoin block h
	2.	G_Z has not been replaced or restarted without detection
	3.	Any descendant state implicitly inherits this lineage

No further guarantees are implied.

⸻

3. Composition with Header-Only Verification

Header-only verification allows a verifier to:

	•	track consensus progression
	•	validate cryptographic linkage between headers
	•	avoid replaying transactions or state transitions

Without GALV:
A header-only verifier must trust its bootstrap source for genesis correctness.

With GALV:
The verifier can independently confirm that the header chain descends from a genesis whose commitment is externally anchored.

Effect:

	•	Bootstrap trust is reduced to Bitcoin’s security assumptions
	•	A verifier joining late or intermittently can still validate origin correctness

GALV does not change header verification mechanics; it constrains their origin.

⸻

4. Composition with Bounded Inclusion

Bounded inclusion replaces transaction identity proofs with effect-equivalence proofs bounded by accessed state.

This enables:

	•	verification cost independent of global throughput
	•	local verification of state effects

Without GALV:
A verifier can validate that an effect is consistent with some chain, but not whether that chain’s origin is authentic.

With GALV:
Every accepted effect is transitively linked to a genesis whose existence and timing are externally fixed.

Effect:

	•	Local state proofs inherit a globally verifiable lineage
	•	A malicious fork cannot fabricate an alternative origin without breaking Bitcoin anchoring

Bounded inclusion remains local; GALV provides global context.

⸻

5. Composition with Minimal State Frontier Verification

Minimal state frontier verification bounds verifier memory by retaining only a rolling window of recent commitments.

This yields:

	•	finite memory verification
	•	local temporal coherence
	•	acceptance of historical incompleteness

Without GALV:
A verifier that drops history cannot independently prove that its chain was not restarted prior to its frontier window.

With GALV:
Even if all pre-frontier data is forgotten, the verifier can still assert:

	•	this frontier descends from a genesis anchored to Bitcoin
	•	the chain’s lineage is continuous from that anchor

Effect:

	•	Finite memory verification does not imply finite trust
	•	Long-range restart attacks are structurally constrained

GALV compensates for what bounded memory necessarily discards.

⸻

6. Why Bitcoin Anchoring Matters for Edge Verifiers

Edge verifiers (browsers, mobile clients, intermittently connected devices) face three constraints:

	1.	limited storage
	2.	unreliable connectivity
	3.	adversarial bootstrap environments

GALV addresses a failure mode common to all three:

silent chain restarts and origin equivocation.

Because Bitcoin provides:

	•	global timestamping
	•	immutable history
	•	independent security assumptions

a verifier can defer trust to Bitcoin once, rather than continuously trusting network peers.

This makes GALV especially relevant where:

	•	verifiers join late
	•	verifiers go offline for extended periods
	•	consensus participants are not continuously observable

⸻

7. Interpretation Rule

When composed with other primitives, GALV means:

“The verified state descends from a genesis that is cryptographically bound to an immutable external timeline.”

It does not mean:

	•	the state is correct
	•	the execution was valid
	•	the data was available
	•	the chain is canonical

Those properties must be supplied elsewhere.

⸻

8. Summary

GALV is best understood as a foundational trust primitive.

It:

	•	anchors lineage
	•	fixes origin
	•	constrains equivocation

It deliberately composes with — but does not replace —
header-only verification, bounded inclusion, and minimal state frontier verification.

Its value lies not in expanding verification guarantees, but in making existing guarantees meaningful for verifiers that cannot afford full history or continuous trust.
