# Bitcoin Header Relay Protocol

**Phase**: 2 — Header Networking & Data Ingestion
**Status**: Exploratory / Research Draft

---

## 1. Overview

This specification defines a protocol for distributing Bitcoin block headers across the Zenon network. The protocol enables nodes to obtain Bitcoin header data for SPV verification while mitigating eclipse attacks through threshold-based tip acceptance.

---

## 2. Design Goals

### 2.1 Primary Goals

1. **Header Availability**: Nodes can obtain recent Bitcoin headers
2. **Eclipse Resistance**: No single source can dictate the canonical tip
3. **Efficiency**: Minimal bandwidth for header distribution
4. **Compatibility**: Works with existing Zenon P2P infrastructure

### 2.2 Non-Goals

- Full Bitcoin node functionality
- Transaction relay
- Block body distribution
- Bitcoin consensus participation

---

## 3. Protocol Architecture

### 3.1 Deployment Options

**Option A: P2P Protocol Extension**
- Extends Zenon's existing P2P layer
- Headers distributed via gossip
- Integrated with node software

**Option B: Sidecar Service**
- Separate process alongside Zenon node
- Communicates via local API
- Independent upgrade cycle

**Recommendation**: Start with Option A (P2P extension) for tighter integration.

### 3.2 Participant Roles

| Role | Description | Requirements |
|------|-------------|--------------|
| Source | Provides headers from Bitcoin network | Bitcoin P2P connection |
| Relay | Forwards headers between Zenon nodes | Standard Zenon node |
| Consumer | Uses headers for SPV verification | Header storage |

A node may fulfill multiple roles simultaneously.

---

## 4. Message Types

### 4.1 Message Overview

| Message | Direction | Purpose |
|---------|-----------|---------|
| `BtcHeaders` | broadcast | Announce new headers |
| `GetBtcHeaders` | request | Request header range |
| `BtcHeadersResponse` | response | Deliver requested headers |
| `BtcTipAnnounce` | broadcast | Announce current tip |
| `GetBtcTip` | request | Request current tip |

### 4.2 BtcHeaders

Announces one or more new Bitcoin headers.

```
BtcHeaders {
    headers:    bytes[]    // Array of 80-byte headers
    height:     u32        // Height of first header
    source_id:  bytes32    // Source node identifier
    timestamp:  u64        // Message timestamp
    signature:  bytes64    // Source signature
}
```

**Constraints**:
- Max 2016 headers per message
- Headers must be sequential
- Source must sign the message

### 4.3 GetBtcHeaders

Requests headers in a height range.

```
GetBtcHeaders {
    start_height: u32      // First header requested
    count:        u16      // Number of headers (max 2016)
    locator:      bytes32  // Optional: known block hash for validation
}
```

### 4.4 BtcHeadersResponse

Response to `GetBtcHeaders`.

```
BtcHeadersResponse {
    request_id: u64        // Matches request
    headers:    bytes[]    // Requested headers
    height:     u32        // Height of first header
}
```

### 4.5 BtcTipAnnounce

Announces the node's view of the Bitcoin tip.

```
BtcTipAnnounce {
    tip_hash:   bytes32    // Block hash of tip
    height:     u32        // Tip height
    chain_work: bytes32    // Cumulative chainwork
    source_id:  bytes32    // Source identifier
    timestamp:  u64        // Announcement time
    signature:  bytes64    // Source signature
}
```

### 4.6 GetBtcTip

Requests current tip from a peer.

```
GetBtcTip {
    request_id: u64
}
```

---

## 5. Threshold Relaying

### 5.1 Mechanism

A node accepts a Bitcoin tip $\hat{t}$ as canonical only if observed from at least $k$ independent sources:

$$
| \{s_j : \text{tip}(s_j) = \hat{t}\} | \ge k
$$

### 5.2 Source Independence

Sources are considered independent if they:
- Have distinct network identities
- Connect to different Bitcoin nodes (if known)
- Are not controlled by the same operator

### 5.3 Threshold Selection

| Threshold $k$ | Eclipse Resistance | Latency | Use Case |
|---------------|-------------------|---------|----------|
| 1 | Minimal | Lowest | Trusted environment |
| 3 | Moderate | Low | Standard operation |
| 5 | High | Moderate | High-value verification |
| 7+ | Very high | Higher | Maximum security |

**Recommendation**: Default $k = 3$ with configurable override.

### 5.4 Tip Tracking

```
TipTracker {
    tips:         Map<bytes32, TipRecord>    // tip_hash -> record
    sources:      Map<bytes32, bytes32>      // source_id -> tip_hash
    threshold:    u16                         // Required confirmations
    current_tip:  bytes32                     // Accepted canonical tip
}

TipRecord {
    tip_hash:     bytes32
    height:       u32
    chain_work:   bytes32
    source_ids:   Set<bytes32>               // Sources announcing this tip
    first_seen:   u64                        // Timestamp
}
```

### 5.5 Tip Acceptance Algorithm

```
OnTipAnnounce(announce):
    # Validate signature
    if not verify_signature(announce):
        return REJECT

    tip_hash = announce.tip_hash
    source_id = announce.source_id

    # Update tip record
    if tip_hash not in tips:
        tips[tip_hash] = TipRecord(tip_hash, announce.height, announce.chain_work)

    tips[tip_hash].source_ids.add(source_id)
    sources[source_id] = tip_hash

    # Check threshold
    if len(tips[tip_hash].source_ids) >= threshold:
        # Compare chainwork with current tip
        if tips[tip_hash].chain_work > tips[current_tip].chain_work:
            current_tip = tip_hash
            emit TipAccepted(tip_hash)
```

---

## 6. Eclipse Mitigation

### 6.1 Attack Model

An eclipse attacker attempts to:
1. Control all of a node's header sources
2. Feed a false Bitcoin chain
3. Enable false SPV proofs

### 6.2 Defense Mechanisms

**Threshold Relaying**
- Requires $k$ independent sources to agree
- Attacker must compromise $k$ sources

**Source Diversity**
- Prefer sources from different network segments
- Track source reliability history
- Rotate sources periodically

**Chainwork Comparison**
- Accept higher-work chains only
- Attacker must produce real PoW

**External Validation**
- Optional: Cross-check with external sources (APIs, other networks)
- Fallback for suspicious disagreements

### 6.3 Detection Heuristics

| Indicator | Action |
|-----------|--------|
| Tip disagreement among sources | Log warning, increase threshold |
| Sudden chainwork drop | Reject, investigate |
| Single source providing all headers | Seek additional sources |
| Headers without PoW | Immediate rejection |

---

## 7. Header Storage

### 7.1 Storage Structure

```
HeaderStore {
    headers:       Map<bytes32, BitcoinHeader>  // hash -> header
    by_height:     Map<u32, bytes32>            // height -> hash
    chain_tips:    Set<bytes32>                 // Known chain tips
    main_chain:    bytes32                      // Current main chain tip
    genesis:       bytes32                      // Bitcoin genesis hash
}
```

### 7.2 Retention Policy

| Policy | Headers Retained | Use Case |
|--------|------------------|----------|
| Minimal | Last 2016 (1 difficulty period) | Resource-constrained |
| Standard | Last 10,000 (~10 weeks) | Normal operation |
| Extended | Last 100,000 (~2 years) | Historical verification |
| Full | All headers since genesis | Archival |

**Recommendation**: Standard retention with on-demand fetching for older headers.

### 7.3 Storage Size

| Retention | Headers | Size |
|-----------|---------|------|
| Minimal | 2,016 | ~157 KB |
| Standard | 10,000 | ~781 KB |
| Extended | 100,000 | ~7.6 MB |
| Full | ~850,000 | ~66 MB |

---

## 8. Synchronization

### 8.1 Initial Sync

New nodes synchronize headers from genesis or a checkpoint:

```
1. Request headers from peers using GetBtcHeaders
2. Validate each header (PoW, linkage)
3. Track chainwork
4. Accept chain with maximum work
5. Enter steady-state mode
```

### 8.2 Checkpoint Bootstrap

To accelerate initial sync:
- Start from a known checkpoint (height, hash)
- Verify checkpoint hash matches expected value
- Sync forward from checkpoint

**Checkpoints** (example):
```
Block 800,000: 00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054
Block 850,000: [TBD when reached]
```

### 8.3 Steady-State

After initial sync:
- Listen for `BtcHeaders` broadcasts
- Process new headers as they arrive
- Track multiple tips during reorgs
- Apply threshold logic for tip acceptance

---

## 9. Peer Management

### 9.1 Peer Selection

Prefer peers that:
- Have been reliable header sources
- Are geographically diverse
- Respond quickly to requests
- Provide consistent tip announcements

### 9.2 Peer Scoring

```
PeerScore {
    headers_provided:  u32     // Headers successfully provided
    invalid_headers:   u32     // Invalid headers sent
    response_time:     u32     // Average response time (ms)
    tip_accuracy:      f32     // % of tips matching consensus
    last_active:       u64     // Last interaction timestamp
}
```

### 9.3 Ban Conditions

| Condition | Duration |
|-----------|----------|
| Invalid PoW header | 24 hours |
| Broken chain linkage | 24 hours |
| Repeated stale tips | 1 hour |
| Timeout on requests | 10 minutes |

---

## 10. Integration with Zenon P2P

### 10.1 Message Routing

Bitcoin header messages use Zenon's P2P layer:
- Same connection management
- Same encryption/authentication
- Separate message namespace (`btc.*`)

### 10.2 Gossip Behavior

`BtcHeaders` and `BtcTipAnnounce` messages:
- Propagated to all connected peers
- Deduplicated by message hash
- TTL-limited to prevent loops

### 10.3 Priority

Header messages have lower priority than:
- Momentum propagation
- Account-block propagation
- Pillar messages

---

## 11. Security Considerations

### 11.1 DoS Protection

- Rate limit header messages per peer
- Maximum message size enforced
- Validation before propagation

### 11.2 Sybil Resistance

- Source independence verification
- Stake-based source weighting (optional)
- IP-based diversity checks

### 11.3 Privacy

- Header requests don't reveal specific transactions
- General chain sync is not privacy-sensitive
- Consider Tor/privacy routing for source diversity

---

## 12. Metrics and Monitoring

### 12.1 Operational Metrics

| Metric | Description |
|--------|-------------|
| `btc_tip_height` | Current accepted Bitcoin height |
| `btc_tip_sources` | Sources confirming current tip |
| `btc_header_latency` | Time from Bitcoin block to receipt |
| `btc_peer_count` | Active header relay peers |
| `btc_sync_status` | Sync progress (%) |

### 12.2 Alerting Conditions

- Tip height stalled (no new blocks)
- Source count below threshold
- Chain reorg detected
- Header validation failures

---

## 13. Future Extensions

### 13.1 Compact Header Encoding

Reduce bandwidth with delta encoding:
- Only transmit changing fields
- Previous block hash implied by linkage
- Potential 40-50% size reduction

### 13.2 Header Commitments in Momentum

Include Bitcoin tip commitment in Momentum:
- Global consensus on Bitcoin state
- Enables fraud proofs against stale tips
- Requires governance approval

### 13.3 Light Relay Nodes

Specialized nodes for header relay:
- Minimal Zenon state
- Focus on Bitcoin header distribution
- Lower resource requirements

---

## 14. References

- [Bitcoin SPV Threat Model](../phase-0-foundation/bitcoin-spv-threat-model.md)
- [Bitcoin Header Data Availability](bitcoin-header-availability.md)
- [Bitcoin P2P Protocol](https://developer.bitcoin.org/reference/p2p_networking.html)
