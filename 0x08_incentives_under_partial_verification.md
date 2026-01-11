Incentives Under Partial Verification

Status

Draft / Notes
Non-normative
Builds on: Application Semantics Over Bounded Verification

⸻

Motivation

In a bounded-verification system, incentives cannot assume:

	•	global visibility
	•	instant finality
	•	universal agreement
	•	synchronized knowledge

This note describes how incentives function when truth is local, partial, and time-bounded.

⸻

Core Constraint

Incentives must reward:

	•	correct behavior relative to a verifier’s frontier
	•	not absolute or global correctness

There is no omniscient judge.

⸻

Incentive Units

Rewards and penalties are tied to:

	•	verifiable actions
	•	provable statements
	•	observable behavior

Not intent.
Not global outcomes.

⸻

Local Rationality

Participants optimize for:

	•	their own verification horizon
	•	expected future verification
	•	refusal risk

Rational behavior is contextual, not globally optimal.

⸻

Proof-Linked Rewards

A reward must be claimable only if:

	•	the claimant supplies a valid proof
	•	the proof verifies within the verifier’s frontier
	•	the proof remains consistent until acceptance

Unprovable claims are worthless.

⸻

Delayed Reward Model

Because verification may be delayed:

	•	rewards may be provisional
	•	settlement may lag execution
	•	acceptance may expire

Applications must model rewards as pending until proven.

⸻

Refusal and Penalty Asymmetry

Failure to prove is not guilt.

Therefore:

	•	penalties must require positive proof of misbehavior
	•	non-proof is not punishable
	•	refusal defaults to no reward, not punishment

This preserves safety under uncertainty.

⸻

Slashing Constraints

Slashing is only safe when:

	•	misbehavior is provable within bounded verification
	•	evidence is independently verifiable
	•	ambiguity is eliminated

If ambiguity remains, slashing must not occur.

⸻

Incentives for Availability

Proof providers are incentivized by:

	•	successful proof delivery
	•	timely responses
	•	consistency across requests

Non-delivery results in lost opportunity, not punishment.

⸻

Free-Rider Tolerance

Some participants may:

	•	consume verification without contributing
	•	appear inactive

This is acceptable.

Forcing contribution under uncertainty creates perverse incentives.

⸻

Economic Finality vs Verification Finality

Economic systems may:

	•	settle probabilistically
	•	hedge against refusal
	•	require confirmations across multiple frontiers

Finality is economic, not absolute.

⸻

Cross-Verifier Incentives

When interacting across verifiers:

	•	rewards require overlapping verified facts
	•	disagreement blocks settlement
	•	reconciliation is explicit

Incentives must tolerate disagreement.

⸻

Offline Incentive Behavior

Offline participants may:

	•	accumulate unclaimed rewards
	•	delay settlement
	•	rejoin with cached proofs

Systems must allow delayed participation without loss of safety.

⸻

MEV Considerations

Bounded verification limits MEV by:

	•	reducing global visibility
	•	fragmenting ordering assumptions
	•	localizing execution

MEV exists, but is scoped.

⸻

Design Principle

Incentives should encourage:

	•	proof production
	•	availability
	•	honesty under partial knowledge

Not speed.
Not dominance.
Not coordination.

⸻

Boundary Statement

No incentive mechanism can guarantee:

	•	global fairness
	•	universal truth
	•	perfect alignment

Bounded verification demands bounded expectations.

⸻

What Follows

Once incentives operate under partial verification, governance must also function without global truth.

The next note addresses this directly:

0x09 — Governance Without Global Consensus
