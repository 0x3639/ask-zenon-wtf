# Transaction Admission Control (Research Note)

Status: exploratory. Not an implementation claim.

## Goal
Describe Zenon-style “feeless” transaction admission as **one control system** with different time horizons, not a stack of unrelated layers.

## Problem Statement
We want:
- spam resistance
- predictable throughput under load
- usability on phones/browsers
without relying on a fee market.

## One Control Loop (Compressed Model)
Transaction admission uses a single feedback loop with three time constants:

1) **Instant throttle (per-tx):** micro-PoW  
2) **Sustained access (per-account):** plasma / resource credits  
3) **Slow global tuning:** parameter adjustment based on observed load

These are not three “layers”. They are one control system viewed at different timescales.

## Minimal Invariant
A transaction is admissible iff the sender satisfies the current admission rule:
- either has sufficient resource credit (plasma), or
- supplies sufficient micro-PoW for the current network condition.

This enforces **rate limiting**, not application intent.

## Why This Isn’t “Mining”
micro-PoW is bounded and device-feasible:
- small enough for phones
- large enough to throttle spam
- adjustable over time

## What a “Supervisor” Would Mean (If It Exists)
Not an executor. Not consensus.
Just a *controller* that proposes/derives parameter updates from observed signals, e.g.:
- mempool pressure / saturation
- state/db growth rate
- average verification cost
- reorg / orphan rates (if relevant)

## Open Questions (What We Want Feedback On)
1) What signals should drive tuning (and which are gameable)?
2) How do we bound worst-case cost for honest users?
3) How do we prevent header/proof/data availability (if any) from becoming a hidden trusted layer?

## What This Note Is Not
- not a roadmap
- not claiming anything exists today
- not claiming uniqueness vs other chains
