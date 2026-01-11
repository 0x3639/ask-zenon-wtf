# Bitcoin Header Data Availability

**Phase**: 2 — Header Networking & Data Ingestion
**Status**: Exploratory / Research Draft

---

## 1. Overview

This document analyzes data availability considerations for Bitcoin headers within the Zenon network. Header availability is prerequisite for SPV verification — without access to the canonical Bitcoin header chain, proofs cannot be validated.

---

## 2. Availability Requirements

### 2.1 What Must Be Available

For SPV verification to function, nodes need:

| Data | Size | Freshness | Criticality |
|------|------|-----------|-------------|
| Recent headers | ~160 KB | Minutes | High |
| Proof headers | Variable | On-demand | Per-verification |
| Chain tip | 80 bytes | Seconds | High |
| Chainwork | 32 bytes | Minutes | High |

### 2.2 Temporal Requirements

**Real-Time Needs**
- Current tip: Updated within minutes of Bitcoin blocks
- Recent headers: Last 6+ blocks for standard confirmations

**Historical Needs**
- Arbitrary headers: For deep confirmation verification
- Checkpoint headers: For validation anchors

### 2.3 Consistency Requirements

- All nodes should converge on the same canonical chain
- Temporary disagreements acceptable during reorgs
- Long-term divergence indicates attack or bug

---

## 3. Data Sources

### 3.1 Source Hierarchy

| Source | Trust Level | Availability | Latency |
|--------|-------------|--------------|---------|
| Direct Bitcoin P2P | Trustless | High | Low |
| Zenon Header Relay | Network trust | High | Low |
| External APIs | API trust | Variable | Variable |
| Hardcoded checkpoints | Build trust | Always | None |

### 3.2 Direct Bitcoin P2P

**Mechanism**: Connect to Bitcoin network, request headers via `getheaders`.

**Advantages**:
- Trustless (verify PoW)
- Authoritative source
- Full history available

**Disadvantages**:
- Requires Bitcoin P2P implementation
- IP address exposure
- Connection overhead

**Recommendation**: Primary source for Zenon full nodes.

### 3.3 Zenon Header Relay

**Mechanism**: Obtain headers from other Zenon nodes via relay protocol.

**Advantages**:
- Integrated with existing infrastructure
- Lower implementation cost
- Shared among nodes

**Disadvantages**:
- Depends on relay honesty
- Eclipse risk if all relays malicious
- Potential latency

**Recommendation**: Primary source for light clients, secondary for full nodes.

### 3.4 External APIs

**Examples**: Blockstream.info, Blockchain.com, Mempool.space

**Advantages**:
- Easy integration
- No P2P complexity
- Often fast

**Disadvantages**:
- Trust the API operator
- Availability depends on third party
- May have rate limits
- Privacy implications

**Recommendation**: Fallback only, with verification.

### 3.5 Hardcoded Checkpoints

**Mechanism**: Embed known block hashes at specific heights in code.

**Advantages**:
- Always available
- No network required
- Acceleration for sync

**Disadvantages**:
- Requires code updates
- Only historical, not current
- Trust the developers

**Recommendation**: Use for sync acceleration, not tip determination.

---

## 4. Failure Modes

### 4.1 Source Unavailability

**Scenario**: No sources respond with headers.

**Impact**:
- Cannot verify new proofs
- Cannot determine current tip
- Existing verified facts remain valid

**Mitigation**:
- Multiple source types
- Cached headers for recent history
- Graceful degradation

### 4.2 Conflicting Tips

**Scenario**: Different sources report different chain tips.

**Causes**:
- Legitimate Bitcoin reorg in progress
- Eclipse attack
- Stale sources
- Network partition

**Resolution**:
- Wait for convergence
- Accept highest-work chain from threshold sources
- Alert on prolonged disagreement

### 4.3 Stale Data

**Scenario**: Sources provide outdated headers.

**Detection**:
- Tip height not advancing
- Timestamps too old
- Known blocks missing

**Mitigation**:
- Track source freshness
- Penalize stale sources
- Seek alternative sources

### 4.4 Malicious Data

**Scenario**: Source provides headers with invalid PoW or fabricated chain.

**Detection**:
- PoW validation fails
- Chain linkage broken
- Chainwork lower than known good chain

**Mitigation**:
- Always validate before accepting
- Ban malicious sources
- Threshold consensus

---

## 5. Storage Considerations

### 5.1 Storage Requirements

| Retention | Headers | Storage | Use Case |
|-----------|---------|---------|----------|
| Minimal | 2,016 | 157 KB | Light clients |
| Standard | 10,000 | 781 KB | Normal nodes |
| Extended | 100,000 | 7.6 MB | Deep verification |
| Full | 870,000+ | 68 MB | Archival |

### 5.2 Storage Strategies

**In-Memory**
- Fast access
- Volatile (lost on restart)
- Suitable for recent headers

**On-Disk**
- Persistent
- Slower access
- Suitable for historical headers

**Hybrid**
- Recent in memory
- Older on disk
- Best of both

### 5.3 Compression

Bitcoin headers have limited entropy. Potential compression:

| Technique | Savings | Complexity |
|-----------|---------|------------|
| Delta encoding | ~30% | Low |
| Dictionary | ~40% | Medium |
| Full compression | ~50% | High |

**Note**: 68 MB uncompressed is already small; compression may not be necessary.

---

## 6. Browser Considerations

### 6.1 Browser Constraints

| Constraint | Limit | Impact |
|------------|-------|--------|
| LocalStorage | 5-10 MB | Limits retention |
| IndexedDB | 50+ MB | Adequate for full history |
| Memory | Variable | Limit in-memory headers |
| Network | Unreliable | Must handle disconnection |

### 6.2 Browser Storage Strategy

```
IndexedDB Schema:
  - headers: { height: u32, hash: bytes32, data: bytes80 }
  - tips: { hash: bytes32, chainwork: bytes32, sources: [] }
  - checkpoints: { height: u32, hash: bytes32 }
```

### 6.3 Browser Data Sources

1. **WebSocket to Zenon relay node**
2. **WebRTC to other browser clients**
3. **REST API fallback**

---

## 7. Sentinel/Sentry Role

### 7.1 Sentinel Header Service

Sentinels could provide:
- Authoritative header feeds
- Historical header queries
- Proof header bundles

### 7.2 Sentry Header Caching

Sentries could:
- Cache headers for their served accounts
- Bundle headers with state proofs
- Reduce redundant fetches

### 7.3 Trust Model

| Node Type | Header Trust |
|-----------|--------------|
| Pillar | Verify directly from Bitcoin |
| Sentinel | Verify from Pillars or Bitcoin |
| Sentry | Obtain from Sentinels |
| Light Client | Obtain from Sentries |

---

## 8. Availability Attacks

### 8.1 Withholding Attack

**Attack**: Malicious nodes refuse to provide headers.

**Impact**: Victim cannot verify proofs.

**Defense**:
- Multiple independent sources
- Reputation tracking
- Source rotation

### 8.2 Eclipse Attack

**Attack**: Attacker controls all of victim's header sources.

**Impact**: Victim accepts false chain.

**Defense**:
- Threshold relaying
- Source diversity requirements
- External validation

### 8.3 DoS Attack

**Attack**: Flood header relay with invalid data.

**Impact**: Overwhelm processing, delay legitimate headers.

**Defense**:
- Rate limiting
- Validate before relay
- Proof-of-work on requests (optional)

---

## 9. Monitoring and Alerting

### 9.1 Health Metrics

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Sources available | ≥3 | 2 | 0-1 |
| Tip age | <30 min | 30-60 min | >60 min |
| Tip agreement | 100% | 80-99% | <80% |
| Response latency | <1s | 1-5s | >5s |

### 9.2 Alert Conditions

- **No sources available**: Immediate alert
- **Tip stagnation**: Alert after 1 hour
- **Source disagreement**: Alert if persistent
- **Invalid data from trusted source**: Security alert

---

## 10. Open Questions

### 10.1 Optimal Caching Strategy

- How long to cache headers before eviction?
- Should cache be shared across accounts?
- LRU vs height-based eviction?

### 10.2 Cross-Peer Header Verification

- Should nodes cross-check headers with peers?
- How to detect localized eclipse attacks?
- Cost/benefit of redundant verification?

### 10.3 Header Commitment

- Should Momentums commit to Bitcoin tip?
- What are the consensus implications?
- How to handle Bitcoin reorgs?

### 10.4 Incentives for Header Provision

- Should header providers be rewarded?
- How to prevent free-riding?
- Integration with Phase 4 incentive mechanisms?

---

## 11. Recommendations

### 11.1 For Full Nodes

1. Connect to Bitcoin P2P for primary headers
2. Participate in Zenon header relay
3. Maintain standard retention (10,000 headers)
4. Implement threshold tip acceptance

### 11.2 For Light Clients

1. Connect to trusted Sentry/Sentinel for headers
2. Verify PoW on all received headers
3. Maintain minimal retention (2,016 headers)
4. Use WebSocket/WebRTC for real-time updates

### 11.3 For Browsers

1. Store headers in IndexedDB
2. Fetch from multiple sources
3. Validate PoW client-side
4. Cache aggressively, evict by age

---

## 12. Summary

Header data availability is a critical dependency for Bitcoin SPV on Zenon. The recommended approach combines:

1. **Multiple source types** for redundancy
2. **Threshold acceptance** for eclipse resistance
3. **Local validation** for trustlessness
4. **Appropriate retention** for resource efficiency

No single failure mode should prevent SPV verification for a well-connected node.

---

## 13. References

- [Bitcoin Header Relay Protocol](bitcoin-header-relay-protocol.md)
- [Bitcoin SPV Threat Model](../phase-0-foundation/bitcoin-spv-threat-model.md)
- [Browser Light Client Overview](/docs/research/browser-light-client-overview.md)
