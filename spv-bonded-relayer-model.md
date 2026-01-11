# Bonded Relayer Model for Bitcoin SPV

**Phase**: 4 — Incentive Mechanisms
**Status**: Exploratory / Research Draft

---

## 1. Overview

This document specifies an economic incentive model for Bitcoin header relayers and checkpoint submitters. Bonded relayers stake collateral that can be slashed for misbehavior, creating economic alignment between relayer profitability and network security.

**Prerequisites**: This phase assumes correctness mechanisms from Phases 0-3 are operational.

---

## 2. Motivation

### 2.1 Liveness Problem

Phases 0-3 establish correctness: invalid proofs are rejected, fraud is punished. However, they don't ensure:
- Headers are actually relayed
- Checkpoints are submitted for important transactions
- Services remain available during high demand

### 2.2 Solution: Economic Incentives

Bonded relayers provide:
- Guaranteed service availability (or stake forfeiture)
- Economic incentive for honest behavior
- Market-driven pricing for relay services

---

## 3. Relayer Roles

### 3.1 Header Relayer

Provides Bitcoin headers to the network.

**Responsibilities**:
- Connect to Bitcoin network
- Relay new headers promptly
- Respond to header requests
- Maintain header availability

### 3.2 Checkpoint Submitter

Submits verified Bitcoin facts as global checkpoints.

**Responsibilities**:
- Perform local SPV verification
- Submit checkpoints with appropriate bond
- Defend against invalid challenges
- Maintain proof availability during challenge window

### 3.3 Combined Role

A single operator may fulfill both roles, sharing infrastructure costs.

---

## 4. Bond Mechanism

### 4.1 Bond Structure

```
RelayerBond {
    relayer:        Address     // Relayer account
    amount:         u64         // Staked ZNN
    locked_until:   u64         // Momentum height
    role:           RelayerRole // HEADER | CHECKPOINT | BOTH
    registered_at:  u64         // Registration Momentum
    slashed:        u64         // Cumulative slashed amount
    status:         BondStatus  // ACTIVE | EXITING | SLASHED
}
```

### 4.2 Bond Parameters

| Parameter | Symbol | Suggested Value | Rationale |
|-----------|--------|-----------------|-----------|
| Minimum stake | $B_{min}$ | 1,000 ZNN | Barrier to sybil |
| Lock period | $L$ | 10,000 Momentums (~7 days) | Stability |
| Slash fraction | $\alpha$ | 0.1 - 0.5 | Per offense |
| Exit delay | $E$ | 5,000 Momentums (~3.5 days) | Security buffer |

### 4.3 Bond Lifecycle

```
Register(amount) ─────► ACTIVE ─────► Serve
                          │
                          │ RequestExit()
                          ▼
                       EXITING ─────► Wait E Momentums
                          │
                          │ Finalize()
                          ▼
                       WITHDRAWN

      Slash event at any point:
      ACTIVE/EXITING ───► SLASHED
```

---

## 5. Slashing Conditions

### 5.1 Header Relayer Slashing

| Offense | Slash Amount | Detection |
|---------|--------------|-----------|
| Invalid PoW header | 50% of bond | On-chain verification |
| Broken chain linkage | 50% of bond | On-chain verification |
| False tip announcement | 25% of bond | Threshold disagreement |
| Extended unavailability | 10% of bond | Heartbeat timeout |

### 5.2 Checkpoint Submitter Slashing

| Offense | Slash Amount | Detection |
|---------|--------------|-----------|
| Fraud proof upheld | 100% of checkpoint bond | Phase 3 mechanism |
| Repeated invalid submissions | Escalating | Pattern detection |

### 5.3 Slashing Process

```
SlashRelayer(relayer, offense, evidence):
    1. Verify offense evidence
    2. Calculate slash_amount = α(offense) × bond.amount
    3. Deduct slash_amount from bond
    4. Distribute:
       - Reporter reward: 50% of slash_amount
       - Protocol treasury: 50% of slash_amount
    5. If remaining bond < B_min:
       - Force exit relayer
    6. Emit SlashEvent(relayer, offense, slash_amount)
```

---

## 6. Reward Structure

### 6.1 Revenue Sources

| Source | Description |
|--------|-------------|
| Header relay fees | Per-header or subscription fees |
| Checkpoint submission fees | Fee for submitting checkpoints |
| Priority access fees | Premium for faster service |
| Protocol subsidies | Bootstrap incentives |

### 6.2 Header Relay Rewards

**Model A: Per-Header**
- Relayer receives fee per unique header relayed
- First relayer to announce wins
- Encourages speed

**Model B: Subscription**
- Users subscribe to relayer's header feed
- Monthly/periodic fee
- Predictable revenue

**Model C: Protocol Subsidy**
- Protocol pays relayers from treasury
- Based on uptime and accuracy
- Bootstrapping phase only

### 6.3 Checkpoint Rewards

Checkpoint submitters earn:
- User-paid submission fee
- Portion of any interest/staking on bond
- Reputation score affecting future demand

---

## 7. Economic Analysis

### 7.1 Attack Cost

For an attacker to profit from false submissions:

$$
\text{AttackProfit} = \text{Value extracted} - \text{Bond lost} - \text{Reputation cost}
$$

With proper bond sizing:
$$
B \ge \frac{\text{Max exploitable value}}{\alpha}
$$

### 7.2 Relayer Profitability

Break-even condition:
$$
\text{Revenue} \ge \text{Infrastructure cost} + \text{Capital cost of bond} + \text{Risk premium}
$$

Where capital cost = bond × opportunity cost rate.

### 7.3 Market Equilibrium

At equilibrium:
- Marginal relayer earns zero economic profit
- Fees equal marginal cost of service
- Bond requirements prevent undercapitalized entry

---

## 8. Relayer Registry

### 8.1 Registration

```
RegisterRelayer(
    bond_amount:    u64,
    role:           RelayerRole,
    metadata:       RelayerMetadata
) -> RelayerId
```

**RelayerMetadata**:
```
RelayerMetadata {
    name:           string      // Display name
    endpoint:       string      // API endpoint (optional)
    capabilities:   u32         // Bitmask of supported features
    fee_schedule:   FeeSchedule // Published rates
}
```

### 8.2 Discovery

```
// List active relayers
ListRelayers(role: RelayerRole, offset: u32, limit: u32) -> Relayer[]

// Get relayer details
GetRelayer(relayer_id: RelayerId) -> Relayer

// Get relayer reputation
GetRelayerReputation(relayer_id: RelayerId) -> ReputationScore
```

### 8.3 Reputation System

```
ReputationScore {
    headers_relayed:      u64     // Total headers provided
    checkpoints_finalized: u64    // Successfully finalized checkpoints
    challenges_won:       u64     // Defended against false challenges
    slashing_events:      u64     // Times slashed
    uptime_percentage:    f32     // Availability score
    avg_latency_ms:       u32     // Response time
}
```

---

## 9. Fee Market

### 9.1 Dynamic Pricing

Fees can adjust based on:
- Network demand
- Relayer capacity
- Urgency requirements

### 9.2 Fee Structures

**Flat Fee**:
- Fixed price per operation
- Simple, predictable
- May not match demand

**Auction**:
- Users bid for priority
- Efficient price discovery
- Complexity for users

**Tiered**:
- Different service levels
- Standard/Priority/Express
- Balance simplicity and efficiency

### 9.3 Example Fee Schedule

| Service | Standard | Priority |
|---------|----------|----------|
| Header request | 0.1 ZNN | 0.5 ZNN |
| Checkpoint submission | 5 ZNN | 20 ZNN |
| Bulk header sync (1000) | 10 ZNN | 30 ZNN |

---

## 10. Governance

### 10.1 Parameter Governance

Adjustable parameters:
- Minimum bond ($B_{min}$)
- Slash fractions ($\alpha$)
- Lock/exit periods
- Fee caps (if any)

### 10.2 Adjustment Process

1. Proposal submitted with rationale
2. Discussion period
3. Vote by governance mechanism
4. Implementation with notice period

### 10.3 Emergency Actions

For critical issues:
- Emergency slash (verified attack)
- Circuit breaker (mass unavailability)
- Parameter freeze (market manipulation)

---

## 11. Integration with Existing Systems

### 11.1 Pillar Integration

Pillars could serve as relayers:
- Existing infrastructure
- Aligned incentives
- Additional revenue stream

### 11.2 Sentinel Integration

Sentinels as proof-serving relayers:
- Natural extension of role
- Serve SPV proofs alongside Zenon proofs

### 11.3 Plasma Integration

Relayer fees payable via:
- Direct ZNN
- Plasma consumption
- Hybrid models

---

## 12. Security Considerations

### 12.1 Collusion Risk

**Risk**: Relayers collude to submit false data.

**Mitigation**:
- Threshold requirements (Phase 2)
- Geographic/operator diversity requirements
- Maximum market share limits

### 12.2 Stake Centralization

**Risk**: Few large stakers dominate.

**Mitigation**:
- Diminishing returns at scale
- Delegation with slashing pass-through
- Reputation weighted by uptime, not just stake

### 12.3 Long-Range Attacks

**Risk**: Attacker accumulates bonds, executes attack, exits.

**Mitigation**:
- Exit delay period
- Slash after exit (within delay)
- Historical reputation tracking

---

## 13. Implementation Phases

### 13.1 Phase 4a: Basic Bonding

- Bond registration and exit
- Simple slashing for fraud
- Manual fee negotiation

### 13.2 Phase 4b: Fee Market

- Automated fee discovery
- Service level tiers
- Reputation scoring

### 13.3 Phase 4c: Advanced Features

- Delegation
- Insurance pools
- Cross-chain collateral

---

## 14. Open Questions

1. **Bond sizing**: How to determine optimal minimum bond?

2. **Delegation**: Should bond holders delegate to operators?

3. **Insurance**: Should relayers pool risk?

4. **Cross-collateralization**: Can bond cover multiple roles?

5. **Transition**: How to bootstrap from permissionless to bonded?

---

## 15. Summary

The bonded relayer model creates economic incentives for reliable Bitcoin header relay and checkpoint submission. Key elements:

- **Stake requirement**: Skin in the game
- **Slashing**: Punishment for misbehavior
- **Rewards**: Payment for honest service
- **Reputation**: Long-term alignment
- **Governance**: Adaptable parameters

This layer ensures liveness and availability while Phases 0-3 ensure correctness.

---

## 16. References

- [Optimistic Bitcoin Fact Checkpointing](../phase-3-optimistic-layer/optimistic-btc-checkpointing.md)
- [Bitcoin SPV Fraud Proofs](../phase-3-optimistic-layer/bitcoin-spv-fraud-proofs.md)
- [SPV Service Credits](spv-service-credits.md)
- [Dynamic Plasma](/docs/notes/dynamic-plasma.md)
