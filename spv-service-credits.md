# SPV Service Credits

**Phase**: 4 — Incentive Mechanisms
**Status**: Exploratory / Research Draft

---

## 1. Overview

This document specifies a credit-based incentive system for Bitcoin SPV services. Service credits reward accurate header provision and checkpoint submission, creating a reputation layer that complements the bonded relayer model.

---

## 2. Motivation

### 2.1 Beyond Bonds

Bonds punish misbehavior but don't directly reward good behavior. Service credits provide:
- Positive incentives for quality service
- Reputation building over time
- Non-monetary recognition
- Access to premium features

### 2.2 Complementary to Bonding

| Mechanism | Purpose | When Applied |
|-----------|---------|--------------|
| Bond slashing | Punish fraud | On violation |
| Service credits | Reward accuracy | On good service |

---

## 3. Credit Model

### 3.1 Credit Structure

```
ServiceCredit {
    holder:        Address     // Credit holder
    credit_type:   CreditType  // HEADER | CHECKPOINT | GENERAL
    amount:        u64         // Credit balance
    earned_at:     u64[]       // Momentum heights of earnings
    spent:         u64         // Total spent
    expired:       u64         // Total expired
}
```

### 3.2 Credit Types

| Type | Earned By | Spent On |
|------|-----------|----------|
| HEADER | Relaying valid headers | Priority header access |
| CHECKPOINT | Finalizing valid checkpoints | Reduced checkpoint fees |
| GENERAL | Any SPV service | Any SPV feature |

### 3.3 Credit Properties

- **Non-transferable**: Credits stay with earning account
- **Expiring**: Credits expire after inactivity period
- **Tiered**: Credit levels unlock features

---

## 4. Earning Mechanism

### 4.1 Header Relay Credits

Credits earned per header:
$$
C_h = \begin{cases}
C_{base} & \text{if first to relay} \\
C_{base} / 2 & \text{if second to relay} \\
0 & \text{otherwise}
\end{cases}
$$

**Parameters**:
- $C_{base}$ = 10 credits per header

### 4.2 Checkpoint Credits

Credits earned per finalized checkpoint:
$$
C_c = C_{checkpoint} \times (1 + \text{depth\_bonus})
$$

Where depth_bonus increases with confirmation depth:

| Depth | Bonus |
|-------|-------|
| 1-5 | 0% |
| 6-11 | 10% |
| 12+ | 25% |

**Parameters**:
- $C_{checkpoint}$ = 100 credits per checkpoint

### 4.3 Bonus Multipliers

| Condition | Multiplier |
|-----------|------------|
| First valid tip announcement | 2x |
| Consistent uptime (>99%) | 1.5x |
| Long service history (>1 year) | 1.25x |
| Defending valid checkpoint | 3x |

---

## 5. Spending Mechanism

### 5.1 Credit Uses

| Use | Cost | Benefit |
|-----|------|---------|
| Priority header request | 5 credits | Skip queue |
| Reduced checkpoint bond | 50 credits | 10% bond reduction |
| Extended proof storage | 20 credits | 2x storage duration |
| API rate limit increase | 100 credits | 2x rate limit |

### 5.2 Spending Rules

- Credits spent in order of oldest first (FIFO)
- Partial spending allowed
- Minimum spend amounts may apply

### 5.3 Spending Process

```
SpendCredits(holder, credit_type, amount, purpose):
    1. Verify holder has sufficient credits
    2. Verify purpose is valid for credit_type
    3. Deduct amount (oldest first)
    4. Apply benefit
    5. Emit CreditSpent(holder, amount, purpose)
```

---

## 6. Accuracy Incentives

### 6.1 Accuracy Tracking

```
AccuracyRecord {
    relayer:           Address
    valid_headers:     u64      // Headers that passed validation
    invalid_headers:   u64      // Headers that failed
    valid_checkpoints: u64      // Checkpoints that finalized
    challenged_checkpoints: u64 // Checkpoints that were challenged
    accuracy_score:    f32      // Computed accuracy
}
```

### 6.2 Accuracy Score Calculation

$$
\text{Accuracy} = \frac{\text{valid\_headers} + 10 \times \text{valid\_checkpoints}}{\text{total\_headers} + 10 \times \text{total\_checkpoints}}
$$

### 6.3 Accuracy-Based Rewards

| Accuracy | Credit Multiplier |
|----------|-------------------|
| < 95% | 0.5x |
| 95-98% | 1.0x |
| 98-99% | 1.25x |
| > 99% | 1.5x |

---

## 7. Penalty for Inaccuracy

### 7.1 Credit Deduction

For invalid submissions:

| Offense | Credit Penalty |
|---------|----------------|
| Invalid header relay | -50 credits |
| Failed checkpoint | -200 credits |
| Fraud proof against | -1000 credits |

### 7.2 Credit Freeze

Repeated violations may freeze credits:
- 3 violations in 1000 Momentums: 500 Momentum freeze
- 5 violations in 1000 Momentums: 2000 Momentum freeze
- 10+ violations: Permanent freeze pending review

---

## 8. Reputation Tiers

### 8.1 Tier Structure

| Tier | Credits Required | Benefits |
|------|------------------|----------|
| Bronze | 0-999 | Standard access |
| Silver | 1,000-9,999 | 10% fee discount |
| Gold | 10,000-99,999 | 25% fee discount, priority queue |
| Platinum | 100,000+ | 50% fee discount, dedicated support |

### 8.2 Tier Maintenance

- Tiers based on cumulative lifetime credits
- Tiers don't decrease (locked once achieved)
- Except: Platinum revoked for fraud

### 8.3 Tier Benefits

**Silver**:
- 10% discount on checkpoint bonds
- Basic API access

**Gold**:
- 25% discount on checkpoint bonds
- Priority header relay
- Extended proof storage

**Platinum**:
- 50% discount on checkpoint bonds
- Dedicated infrastructure queue
- Early access to new features
- Governance participation rights

---

## 9. Integration with Plasma

### 9.1 Credit-to-Plasma Conversion

Optional: Convert excess credits to Plasma:

$$
\text{Plasma} = \text{Credits} \times R_{conversion}
$$

**Parameters**:
- $R_{conversion}$ = 10 Plasma per credit

### 9.2 Plasma for Credits

Not allowed (prevents purchase of reputation).

### 9.3 Credit Priority

When spending on SPV services:
1. Use available credits first
2. Fall back to Plasma if insufficient credits
3. Reject if neither available

---

## 10. Governance Considerations

### 10.1 Adjustable Parameters

| Parameter | Current | Governance Controlled |
|-----------|---------|----------------------|
| $C_{base}$ (header credit) | 10 | Yes |
| $C_{checkpoint}$ (checkpoint credit) | 100 | Yes |
| Tier thresholds | Various | Yes |
| Conversion rate | 10 | Yes |
| Expiration period | 100,000 Momentums | Yes |

### 10.2 Credit Inflation

**Risk**: Unlimited credit issuance devalues system.

**Controls**:
- Cap daily credit issuance
- Increase thresholds over time
- Burn portion of spent credits

### 10.3 Abuse Prevention

**Sybil Attack**: Create many accounts to farm credits.

**Defense**:
- Minimum stake to earn credits
- Per-account rate limits
- Long-term reputation value

---

## 11. Credit Lifecycle

### 11.1 Issuance

```
Earning action ──► Credit created ──► Added to balance
                                           │
                                           ▼
                                      Available for use
```

### 11.2 Expiration

Credits expire if unused:
- Expiration period: 100,000 Momentums (~70 days)
- Clock resets on any account activity
- Warning issued before expiration

### 11.3 Spending

```
Request service ──► Check balance ──► Deduct credits
                         │                  │
                         │                  ▼
                         │            Apply benefit
                         │                  │
                         ▼                  ▼
                   Insufficient ──► Reject or use Plasma
```

---

## 12. Reporting and Analytics

### 12.1 Credit Dashboard

Relayers can view:
- Current credit balance by type
- Earning history
- Spending history
- Tier status
- Accuracy metrics

### 12.2 Network Metrics

Aggregate statistics:
- Total credits in circulation
- Credits earned per epoch
- Credits spent per epoch
- Tier distribution

### 12.3 Leaderboard

Public ranking by:
- Total credits earned (lifetime)
- Accuracy score
- Active credit balance

---

## 13. Implementation Notes

### 13.1 Storage

```
CreditStore {
    balances:     Map<Address, CreditBalance>
    history:      Map<Address, CreditEvent[]>
    tiers:        Map<Address, Tier>
    accuracy:     Map<Address, AccuracyRecord>
}
```

### 13.2 Event Types

```
enum CreditEvent {
    EARNED { amount: u64, reason: string, momentum: u64 }
    SPENT { amount: u64, purpose: string, momentum: u64 }
    EXPIRED { amount: u64, momentum: u64 }
    PENALTY { amount: u64, reason: string, momentum: u64 }
}
```

### 13.3 Query Interface

```
GetCreditBalance(address) -> CreditBalance
GetCreditHistory(address, limit) -> CreditEvent[]
GetTier(address) -> Tier
GetAccuracy(address) -> AccuracyRecord
GetLeaderboard(limit) -> LeaderboardEntry[]
```

---

## 14. Open Questions

1. **Transferability**: Should credits ever be transferable?

2. **Delegation**: Can credits be delegated with stake?

3. **Cross-service credits**: Use SPV credits for other Zenon services?

4. **Monetary value**: Should credits have explicit market value?

5. **Decay vs expiration**: Gradual decay or cliff expiration?

---

## 15. Summary

Service credits create positive incentives for reliable SPV service:

- **Earning**: Rewards for accurate header relay and checkpoint submission
- **Spending**: Discounts and priority access
- **Tiers**: Long-term reputation building
- **Accuracy**: Multipliers for consistent quality
- **Integration**: Works alongside bonds and Plasma

The system encourages sustained, high-quality participation in the SPV network.

---

## 16. References

- [Bonded Relayer Model](bonded-relayer-model.md)
- [Optimistic Bitcoin Fact Checkpointing](../phase-3-optimistic-layer/optimistic-btc-checkpointing.md)
- [Dynamic Plasma](/docs/notes/dynamic-plasma.md)
