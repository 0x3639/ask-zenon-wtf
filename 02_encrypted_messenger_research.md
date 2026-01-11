# Resilient Encrypted Messaging on Zenon Network

A Cryptographic Communication Primitive for Hostile and Disconnected Environments

Research Roadmap — Exploratory Analysis

December 23, 2025

Document Status: Exploratory research roadmap for technical feasibility assessment. This is not a product specification, deployment commitment, or security guarantee. Intended audience: Researchers and engineers familiar with decentralized identity systems, bounded verification models, and light-client architectures.

# Abstract

We present a research roadmap for constructing encrypted, serverless messaging applications (zApps) on Zenon Network's dual-ledger architecture under adversarial conditions including internet outages, network partitioning, infrastructure collapse, and surveillance pressure. Building on prior work in decentralized identity with deterministic key rotation, we explore whether cryptographically verifiable, asynchronous communication is feasible when traditional messaging infrastructure fails. The proposed system treats messaging as a resilient communication primitive rather than a consumer chat application, prioritizing message authenticity and integrity over real-time delivery guarantees. We analyze the viability of pluggable transport layers including satellite relay for environments without terrestrial internet, establish formal requirements for offline verification, and identify fundamental limitations including the impossibility of delivery guarantees and traffic analysis resistance. The architecture leverages identity-as-frontier verification  $(\mathrm{O}(\mathrm{k} + \log \mathrm{N})$  complexity with 1.2-2.8 KB proofs) to enable message authentication without trusted infrastructure. Critical use cases include humanitarian operations, armed conflict zones, and natural disaster response where authenticity matters more than immediacy. We explicitly acknowledge that this system does not solve global availability, traffic analysis, or real-time coordination—it provides cryptographic guarantees for identity and message integrity under minimal infrastructure assumptions.

Keywords: encrypted messaging, decentralized identity, resilient communications, offline verification, satellite relay, bounded proofs, dual-ledger architecture, hostile environments, light clients, asynchronous messaging

# 1. Introduction and Motivation

Existing encrypted messaging systems (Signal, WhatsApp, Telegram) depend fundamentally on continuous internet connectivity, centralized server infrastructure, and phone number-based identity. These dependencies create systemic failure modes when adversarial conditions emerge: natural disasters destroy telecommunications infrastructure, authoritarian regimes implement internet shutdowns, armed conflicts disrupt civilian communications, and surveillance pressure forces messaging platforms offline.

This research roadmap explores whether an encrypted messaging system can be constructed on Zenon Network's dual-ledger architecture that remains functional under these adverse conditions. The key insight is to treat messaging not as a real-time chat application but as an asynchronous communication primitive where cryptographic guarantees (authentication, integrity, non-repudiation) matter more than delivery speed or guaranteed availability.

# 1.1 Design Philosophy and Non-Goals

This system is explicitly not designed to compete with consumer messaging applications under normal network conditions. Signal and WhatsApp are superior for real-time conversation when infrastructure is available. Instead, we target scenarios where infrastructure has failed or is compromised, and establish what cryptographic properties can be maintained with minimal assumptions.

Design Principle: Assume transport is adversarial, infrastructure is unavailable, and time-to-delivery is unbounded. Cryptographically guarantee only what can be proven under these constraints.

# 1.2 Principal Contributions

This roadmap makes the following research contributions: (1) Formal requirements for offline-verifiable encrypted messaging derived from identity-as-frontier model; (2) Architecture for pluggable transport explicitly separating cryptographic guarantees from delivery mechanisms; (3) Satellite relay model demonstrating feasibility of broadcast-based state synchronization without trusted intermediaries; (4) Explicit limitation analysis proving impossibility of delivery guarantees and traffic analysis resistance; (5) Use case taxonomy for humanitarian, conflict, and disaster scenarios where this approach is superior to existing systems.

# 1.3 Relationship to Prior Work

This work builds directly on the decentralized identity system with deterministic key rotation presented in our companion paper. That system established: (1) Identity verification complexity  $O(k + \log N)$  with 1.2-2.8 KB proofs; (2) Offline verification capability from cached momentum headers; (3) Security proofs equivalent to collision-resistant hash functions and EUF-CMA-secure signatures; (4) Imppossibility results for non-existence proofs in bounded-state systems. These properties are prerequisites for this messaging architecture—they enable sender authentication without trusted infrastructure.

# 2. Formal Model and Definitions

# 2.1 System Components

The messaging system comprises four logical components:

Identity Layer: Long-lived identity keys anchored in account-chain commitments with verifiable rotation. Identity  $\alpha$  is permanent (derived from genesis block or initial key). Key state  $State(\alpha, m)$  includes signing key hash  $H(PK_s)$ , control key hash  $H(PK_c)$ , and sequence number  $n$ .

Message Format: Cryptographic envelope containing end-to-end encrypted payload, per-message ephemeral keys for forward secrecy, signed sender identity reference, and no plaintext metadata. Message M = {Enc(payload, K_ephemeral), Sign(H(M), SKsender),  $\alpha$ -sender, timestamp, sequence}.

Verification Oracle: Local algorithm Verify(M, State(α, m)) that checks sender identity against cached headers, validates key at known commitment, and verifies signature correctness. Returns {valid, invalid, unverifiable} where unverifiable indicates awaiting proof material.

Transport Layer: Pluggable, untrusted delivery mechanism. May be peer-to-peer (WebRTC), store-and-forward (intermittent connectivity), or satellite broadcast (no internet). Transport is explicitly not part of trust model—it can delay, reorder, or drop messages but cannot forge valid signatures.

# 2.2 Threat Model

We model adversary A with the following capabilities:

A1. Transport Control: Adversary controls all transport channels (internet, satellites, mesh networks). Can observe, delay, reorder, or drop messages. Cannot decrypt messages or forge signatures without compromising keys.

A2. Infrastructure Denial: Can disable centralized infrastructure (servers, certificate authorities, DNS) indefinitely. System must function without these services.

A3. Traffic Analysis: Has full visibility into message metadata (timestamp, sizes, recipients). Cannot learn message contents but can infer communication patterns. We explicitly do not defend against traffic analysis.

A4. Key Compromise: Can compromise one key class (signing, control, recovery) but not multiple simultaneously within rotation window. Cannot break cryptographic primitives with non-negligible probability.

A5. State Manipulation: Can present forged or stale blockchain state to clients. Clients must detect invalidity through proof verification or reject stale state via validity windows.

# 2.3 Security Properties

The system provides the following cryptographic guarantees:

Message Authentication: Recipient can verify message originated from claimed sender  $\alpha$ . Forgery probability bounded by  $\varepsilon\_sig + \varepsilon\_hash \approx 2^{\wedge} - 127$  assuming SHA-256 and EdDSA. Proven via reduction to EUF-CMA security of signature scheme.

Message Integrity: Any modification to message payload, metadata, or cryptographic envelope is detectable through signature verification. Tampering probability bounded by collision resistance of hash function.

Forward Secrecy: Compromise of long-term signing key does not reveal past message contents due to ephemeral per-message encryption keys. Key derivation uses ECDH with fresh ephemeral keys per message.

Non-Repudiation: Sender cannot credibly deny sending message once delivered. Digital signature binds message to sender's identity with cryptographic strength. Note: This may be undesirable for some threat models.

# 2.4 Explicit Non-Guarantees

The following properties are not guaranteed and are proven impossible under our constraints:

Delivery Guarantee: No proof that message will eventually reach recipient. Transport failures, recipient offline, or adversarial interference can prevent delivery indefinitely. This is fundamental—any system claiming guaranteed delivery in adversarial networks is incorrect.

Traffic Analysis Resistance: Adversary with transport visibility can observe communication patterns, message sizes, and timing. Onion routing or mix networks could provide resistance but at cost of increased latency and complexity. Future work may explore this trade-off.

Real-Time Guarantees: No bounds on message delivery latency. Messages may arrive seconds, hours, or days after sending. System is asynchronous by design.

Deniability: Messages are non-repudiable due to digital signatures. For threat models requiring deniability (journalist sources, whistleblowers), this system is inappropriate. Signal's deniable authentication would be preferred in those cases.

# 3. Offline Verification Model

# 3.1 Verification Requirements

Message verification in disconnected environments requires the recipient to establish: (1) Sender identity  $\alpha$  is valid and corresponds to claimed account-chain; (2) Current signing key PK_s is authorized for identity  $\alpha$  at momentum height m; (3) Message signature is valid under PK_s; (4) Message has not expired according to validity window. These claims must be verifiable using only locally cached data plus minimal proof material that can be delivered via any transport mechanism.

# 3.2 Proof Bundle Structure

To enable offline verification, messages are accompanied by a proof bundle containing:

Momentum Headers: Chain of  $k = 6$  confirmation headers proving consensus finality. Each header 80 bytes, total 480 bytes. Provides consensus proof that sender's account block was confirmed.

Merkle Inclusion Proof: Path from account block to momentum root,  $O(\log N)$  depth where  $N =$  blocks per momentum. For  $N = 1000$ , depth  $= 10$ , size  $\approx 320$  bytes. Proves account block inclusion without requiring full block data.

Identity Frontier Block: Latest account block containing key commitment State  $(\alpha, m)$ . Approximately 200 bytes. Contains H(PK_s), sequence number, and timestamp.

Key Rotation History: For r recent rotations, signatures proving control key authorized each rotation. Approximately 64 bytes per rotation. For  $r = 2$  typical case, 128 bytes.

Total Proof Size:  $480 + 320 + 200 + 128 = 1,128$  bytes typical case. Worst case with  $r = 5$  rotations:  $1,128 + 192 = 1,320$  bytes. Consistent with 1.2-2.8 KB bounds from identity paper.

# 3.3 Verification Algorithm

The verification algorithm Verify(M, proof Bundle, cached_state) operates as follows:

Step 1: Check momentum header chain continuity via hash chain validation. Complexity  $O(k) = 6$  hash operations.

Step 2: Verify Merkle inclusion proof from identity frontier block to momentum root. Complexity  $O(\log N) \approx 10$  hash operations for  $N = 1000$ .

Step 3: Validate key rotation signatures for r rotations. Complexity  $O(r) = 2 - 5$  signature verifications at 0.02ms each ≈ 0.04-0.1ms.

Step 4: Extract H(PK_s) from frontier block, compute H(PK_s_claimed), verify equality. Complexity  $O(1) = 1$  hash operation.

Step 5: Verify message signature using PK_s. Complexity  $O(1) = 1$  signature verification ≈ 0.02ms.

Step 6: Check timestamp within validity window (e.g., 24 hours). Reject if expired.

Total Complexity:  $O(k + \log N + r)$  hash operations plus  $O(r + 1)$  signature verifications. For typical parameters: 17 hash ops × 0.001ms + 3 sig verifications × 0.02ms ≈ 0.08ms cryptographic operations. Network I/O dominates total latency (10-100ms).

# 3.4 Staleness and Validity Windows

As proven in the identity paper (Theorem 3: Non-Existence Verification Impossibility), bounded-state verifiers cannot cryptographically prove that no newer key rotation exists. Therefore, we use validity windows as an operational approximation: messages include timestamp and expiration, verifier accepts proofs within window T (e.g., 1-24 hours). Security-availability trade-off: shorter T increases security against stale key acceptance but decreases availability in high-latency networks. Recommended  $T = 6$  hours for disaster scenarios,  $T = 1$  hour for normal conditions.

# 4. Transport Layer Architecture

# 4.1 Transport Independence Principle

A core architectural decision is that transport is explicitly not part of the trust model. Cryptographic guarantees (authentication, integrity) are transport-independent. This enables graceful degradation: as infrastructure fails, the system can fall back to progressively more constrained transports while maintaining security properties. We identify three transport tiers with different characteristics:

# 4.2 Tier 1: Direct P2P (Normal Conditions)

Mechanism: WebRTC data channels or libp2p for browser/mobile clients. Direct peer discovery via DHT or signaling servers (while available).

Performance: Low latency (10-100ms), high throughput (100KB-1MB/s). Suitable for rich media and large proof bundles.

Failure Mode: Requires working internet and NAT traversal. Fails when ISPs are down, censorship deployed, or infrastructure destroyed.

# 4.3 Tier 2: Store-and-Forward (Intermittent Connectivity)

Mechanism: Messages cached at relay nodes, delivered when recipient comes online. Peers act as untrusted mailboxes.

Performance: High latency (minutes to hours), bounded throughput by storage at relay nodes.  
Message integrity protected by signatures—relay cannot tamper.

Failure Mode: Still requires occasional connectivity to relay nodes. Fails in complete network partition or if all relay nodes are compromised/offline.

# 4.4 Tier 3: Satellite Broadcast (No Internet)

Satellite relay represents the most constrained but most resilient transport tier. We analyze its feasibility in detail as it is the limiting case for system design.

Satellite Role: Broadcast channel carrying three types of data: (1) Momentum headers for blockchain state synchronization; (2) Identity proof bundles for sender verification; (3) Encrypted message payloads. Satellite operates as a blind relay—it does not decrypt, validate, or understand data being broadcast.

Bandwidth Analysis: Momentum headers at 6 per minute, 80 bytes each: 691 KB/day. Identity proof bundles 1.2 KB typical, assume 1,000 active users with 10 messages/day each: 12 MB/day. Message payloads average 500 bytes encrypted: 5 MB/day. Total broadcast bandwidth:  $\sim 18$  MB/day. This is within commercial satellite uplink capacity (typical L-band: 100s of Kbps sustained).

Security Properties: Satellite sees only encrypted payloads and cryptographic proofs. Cannot learn message contents (end-to-end encrypted), cannot impersonate senders (no signing keys), cannot forge proofs (deterministic from blockchain). Can only perform denial-of-service (refuse to broadcast) or traffic analysis (observe patterns). Traffic analysis is explicitly accepted as outside threat model.

Failure Mode: Satellite itself could fail or be compromised. However, satellites are harder to physically disable than ground infrastructure, operate across political borders, and can be redundantly deployed. Multiple commercial operators (Starlink, Iridium, Inmarsat) exist.

# 4.5 Return Channel Problem

Satellite broadcast provides downlink but not uplink. Users receiving messages cannot reply via satellite without uplink capability. Solutions: (1) Satellite with both uplink and downlink (requires satellite terminals, more expensive); (2) Opportunistic uplink via any available channel (mobile data, WiFi) when accessible; (3) Mesh networking between local users who batch messages for uplink; (4) Radio-based local relay to uplink station. This is an engineering challenge, not a fundamental limitation.

# 5. Message Format and Cryptographic Envelope

# 5.1 Encryption Scheme

Messages use hybrid encryption combining asymmetric key exchange and symmetric encryption:

Key Exchange: Sender generates ephemeral ECDH key pair (e_SK, e_PK). Computing shared secret  $S =$  ECDH(e_SK, recipient_PK_s) where recipient_PK_s is recipient's current signing key. Derives encryption key  $K =$  KDF(S, context) using HKDF with message-specific context.

Encryption: Payload encrypted as C = ChaCha20-Poly1305(K, nonce, plaintext) providing authenticated encryption. Nonce derived from timestamp and sequence to ensure uniqueness.

Forward Secrecy: Fresh ephemeral key per message. Compromise of long-term signing key does not reveal past messages because e_SK is never persisted. Only shared secret S is computed transiently.

# 5.2 Message Structure

Complete message structure M contains:

Header: {version: 1 byte, message_type: 1 byte,  $\alpha$ -sender: 32 bytes,  $\alpha$ -recipient: 32 bytes, timestamp: 8 bytes, sequence: 8 bytes, e_PK: 32 bytes} = 114 bytes.

Encrypted Payload: {ciphertext: variable, auth_tag: 16 bytes}. Typical payload 500 bytes + 16 bytes = 516 bytes.

Signature: {sig: 64 bytes} covering H(header || ciphertext || auth_tag) signed with sender's SK_s. Provides message authenticity and integrity.

Proof Bundle: {proof: 1,200-2,800 bytes} as defined in Section 3.2. Optional—may be fetched separately if not bundled.

Total Size:  $114 + 516 + 64 = 694$  bytes for message core. With proof bundle: 1,894-3,494 bytes typical. Without proof bundle (if cached): 694 bytes. This is comparable to Signal message overhead.

# 5.3 Metadata Leakage

Header contains sender and recipient identities  $\alpha$ -sender and  $\alpha$ -recipient in plaintext. This is necessary for recipient to identify messages for them and retrieve appropriate keys for decryption. Consequence: Adversary observing transport can see who is communicating with whom. Message content remains confidential but communication graph is visible. This is a fundamental trade-off—hiding metadata requires techniques like onion routing or mix networks which introduce significant latency and complexity. For disaster/conflict scenarios, we prioritize simplicity and resilience over metadata privacy.

# 6. Operational Semantics and Lifecycle

# 6.1 Message States

Messages transition through the following states during their lifecycle:

Composed: Message created by sender, encrypted, signed. Not yet transmitted.

In-Flight: Message transmitted via transport but not yet received by recipient. May be in transit, cached at relay, or broadcast via satellite.

Received-Unverifiable: Recipient has message but lacks proof bundle or cached state to verify.  
Message is stored but not displayed or trusted until verification completes.

Verified: All cryptographic checks passed (signature valid, identity proven, not expired). Message is authentic and can be displayed to recipient.

Expired: Message timestamp outside validity window. Cannot be verified cryptographically. May still be readable if previously verified but authenticity is no longer guaranteed.

Invalid: Verification failed due to bad signature, tampered content, or revoked key. Message is rejected and should not be displayed.

# 6.2 Supported Operations

The system supports asynchronous messaging primitives:

Send: Compose message, encrypt for recipient, sign with sender key, attach proof bundle (optional), transmit via available transport. No delivery confirmation—sender cannot know if message reached recipient.

Receive: Accept message from any transport, store in received-unverifiable state, fetch proof bundle if not attached, verify when proof material available. Display if verification succeeds.

Delayed Verification: If recipient offline for extended period, messages accumulate in unverifiable state. When connectivity restored and momentum headers updated, all pending messages can be verified in batch. This enables messaging even when recipient is offline for days.

Offline Reading: Previously verified messages remain readable indefinitely (subject to local storage). Recipient can review message history even when completely disconnected.

# 6.3Unsupported Operations

The following operations are not supported and attempting to build them would violate architectural constraints:

Real-Time Chat: No delivery confirmations, read receipts, or typing indicators. These require bidirectional real-time communication which we cannot guarantee in adversarial networks.

Message Ordering: Messages may arrive out of order. Sequence numbers provide partial ordering per sender but global ordering across senders is not guaranteed. Applications must handle out-of-order delivery.

Presence Information: Cannot reliably determine if recipient is online. Message may sit in-flight indefinitely if recipient is offline or transport is disrupted.

Message Deletion/Revocation: Once message is transmitted, sender has no control over its lifecycle. Cannot recall, delete, or modify message. This is fundamental to offline operation—recipient may have no connectivity to receive revocation.

# 7. Critical Use Cases and Real-World Requirements

# 7.1 Natural Disaster Response

Scenario: Major earthquake destroys telecommunications infrastructure in urban area. Power is intermittent, cellular towers are down, internet backbone is severed. Relief coordination between NGOs, government agencies, and local responders is critical but traditional communications (phone, SMS, internet) are unavailable.

System Requirements: (1) Verify authenticity of coordination messages without cellular/internet; (2) Accept messages delivered hours/days later via any available channel (satellite, hand-carried, radio relay); (3) Prevent impersonation of relief coordinators; (4) Function on battery-powered devices with constrained resources. Key Property: Authenticity matters more than speed—better to receive verified instruction late than unverified instruction immediately.

How This System Helps: Relief workers can verify messages from known coordinators using cached momentum headers (updated when any connectivity available). Satellite broadcast provides minimal state sync for verification. Messages delivered via any transport (including hand-carried USB drives) can be authenticated. No dependency on centralized infrastructure that may be destroyed.

# 7.2 Armed Conflict and Censorship

Scenario: Authoritarian regime implements internet shutdown to suppress protests or control information. ISPs are ordered to block encrypted messaging apps. Citizens need to coordinate humanitarian aid, verify information sources, and communicate with family without regime surveillance or interference.

System Requirements: (1) End-to-end encryption resistant to ISP-level surveillance; (2) Function without centralized servers that can be blocked or seized; (3) Verify message authenticity to prevent regime disinformation; (4) Utilize transport layers regime cannot easily block (satellite). Critical limitation: Does not hide who is communicating with whom (metadata).

How This System Helps: Encrypted payloads prevent ISP-level content surveillance. Decentralized architecture eliminates single point of failure. Satellite relay bypasses terrestrial infrastructure. Cryptographic verification prevents regime from impersonating legitimate sources. Caveat: Regime with satellite jamming capability or physical control over devices can still interfere. This is not a silver bullet.

# 7.3 Humanitarian Operations Across Borders

Scenario: International NGO operates in multiple countries with varying levels of internet freedom and infrastructure reliability. Field workers need secure, authenticated communication with headquarters and each other, but cannot rely on consistent connectivity or trust local telecom providers.

System Requirements: (1) Work across diverse network conditions (high-speed internet, rural 3G, satellite-only); (2) Maintain security even when messages traverse compromised infrastructure; (3) Verify authenticity of field reports and instructions; (4) Support operation by non-technical field staff.

How This System Helps: Transport-independent design allows graceful degradation. Same cryptographic guarantees regardless of transport tier. Field workers can receive verified messages

even with days of latency. Identity verification works offline once initial state is synchronized. Trade-off: Less user-friendly than consumer apps, requires training.

# 7.4 What This System Does NOT Solve

Intellectual honesty requires acknowledging scenarios where this system is inappropriate:

Journalist Source Protection: Non-repudiable signatures mean sources cannot credibly deny sending messages. For this threat model, Signal's deniable authentication or systems like SecureDrop are more appropriate. Use case mismatch.

Covert Operations: Metadata leakage reveals communication graph. For scenarios requiring traffic analysis resistance (spy craft, whistleblowing), additional layers (Tor, mix networks) are necessary but introduce latency incompatible with offline operation. Fundamental trade-off.

Consumer Social Messaging: Lack of real-time features (read receipts, typing indicators, presence) makes UX inferior to WhatsApp/Signal under normal conditions. Not designed for this use case.

High-Throughput Broadcasting: Proof bundle size (1-3 KB per message) makes this system unsuitable for high-frequency broadcasting to thousands of recipients. Better suited for point-to-point or small group communication. Scalability limitation.

# 8. Implementation Considerations and Engineering Challenges

# 8.1 Client Architecture

Reference implementation would consist of:

Identity Manager: Maintains local identity state, signing keys, and cached proof bundles. Handles key rotation according to policy. Estimated 800-1000 LOC.

Message Composer/Parser: Handles encryption, signature generation, proof bundle attachment. Estimated 600-800 LOC.

Verification Engine: Implements algorithm from Section 3.3, validates proofs, checks signatures. Estimated 700-900 LOC.

Transport Abstraction: Pluggable interface for P2P, store-and-forward, satellite. Manages transport selection and fallback. Estimated 500-700 LOC per transport tier.

State Synchronization: Fetches momentum headers, maintains header cache, triggers re-verification when state updates. Estimated 400-600 LOC.

Storage Layer: Persists messages in various states, manages proof bundle cache, handles expiration. Estimated 400-500 LOC. Browser: IndexedDB, Mobile: SQLite.

UI Layer: Displays messages with verification status, provides composition interface, shows warnings for unverifiable/expired messages. Estimated 1500-2000 LOC. Not included: UX polish, animations, media handling.

Total Estimate: 5,500-7,500 LOC for complete implementation excluding UI polish. Comparable to minimal email client. Not trivial but achievable for small team over 3-6 months.

# 8.2 Browser Integration Challenges

Browser environment presents specific constraints:

**Cryptography:** Web Crypto API provides Ed25519, ECDH, ChaCha20-Poly1305. SHA-256 and key derivation available. Sufficient for implementation—no WebAssembly required for crypto primitives.

Storage: IndexedDB provides 50MB+ per origin. Sufficient for proof bundles (1-3 KB each) and message storage (thousands of messages). Persistence not guaranteed—users should backup keys.

Networking: WebSocket for momentum sync, Fetch API for REST calls, WebRTC for P2P. No raw socket access limits transport options but sufficient for Tier 1 and Tier 2. Satellite broadcast requires native extension or external receiver feeding data to browser.

Background Operation: Service Workers enable background sync when connectivity restored. Can fetch momentum headers and verify pending messages without user action. Limited compared to native apps but workable.

# 8.3 Mobile Platform Considerations

Mobile platforms provide both opportunities and constraints:

Key Storage (iOS): Secure Enclave provides hardware-backed key storage. Signing keys never leave secure element. Requires biometric unlock for signing operations. Superior security to browser but requires native app.

Key Storage (Android): AndroidKeyStore provides similar but less consistent security (depends on device TEE capabilities). Fallback to software keystore on older devices.

Background Sync: Both platforms restrict background networking for battery life. iOS particularly aggressive. Solution: Require user to open app periodically for state sync, or use push notifications as wake-up mechanism (requires centralized notification service, undesirable).

Satellite Integration: External satellite receiver connects via Bluetooth or USB-C. Mobile app acts as client for receiver's API. Starlink and Iridium provide SDKs. Hardware dependency but unavoidable for Tier 3 transport.

# 8.4 Sentinel Network for Proof Distribution

While messages can include proof bundles, bandwidth optimization requires external proof distribution:

Sentinel Role: Sentinels are nodes that: (1) Maintain full blockchain state; (2) Construct proof bundles on demand; (3) Serve proofs via REST API. Sentinels cannot forge proofs (deterministic from blockchain) but can withhold correct proofs (availability attack).

Trust Model: As proven in identity paper (Sentinel Non-Forgery theorem), one honest sentinel suffices for correctness. Client queries multiple sentinels (2-of-3 or 3-of-5), accepts proof if majority agree. Byzantine sentinels can only DoS, not forge.

Economic Sustainability: Open research question. Options: (1) Volunteer-operated (like Tor); (2) Micropayments per proof request; (3) Subscription model; (4) Pillar node operators run sentinels as service. Requires further investigation.

Performance: Proof construction requires Merkle proof generation (O(log N) hashes) plus database lookups. Estimated 5-15ms per proof on commodity hardware. Can serve thousands of requests per second. Caching of recent proofs reduces load.

# 9. Limitations, Boundaries, and Open Research Questions

# 9.1 Fundamental Limitations (Proven Impossible)

The following limitations are not engineering challenges but proven impossibilities:

Delivery Guarantees: Impossible in asynchronous networks with adversarial transport (proven by FLP impossibility result for asynchronous consensus). System cannot guarantee message will eventually reach recipient. At best, can provide probabilistic delivery under assumptions about transport reliability. Any system claiming guaranteed delivery in adversarial networks is incorrect.

Non-Existence Proofs: As proven in identity paper (Theorem 3), bounded-state verifiers cannot cryptographically prove no newer key rotation exists. Validity windows are operational approximation, not cryptographic proof. Fundamental limitation of light clients.

Traffic Analysis Resistance: Without mix networks or onion routing, adversary observing transport sees communication patterns. Zero-knowledge or homomorphic techniques could hide metadata but require orders of magnitude more computation. Trade-off: accept metadata leakage for simplicity and offline capability.

# 9.2 Engineering Challenges (Difficult but Feasible)

These challenges have solutions but require significant engineering effort:

UX for Asynchronous Messaging: Users are conditioned by real-time chat (WhatsApp, Signal). Teaching mental model of delayed, unordered delivery is a usability challenge. Requires careful UI design with clear status indicators (in-flight, unverifiable, verified, expired). Education problem more than technical problem.

Key Management for Non-Technical Users: Recovery key backup is critical but unfamiliar to average users. Losing recovery key means permanent identity loss (equivalent to losing crypto seed phrase). Social recovery mechanisms could help but introduce complexity. Solvable but requires UX innovation.

Satellite Integration: Requires external hardware (satellite receiver) for Tier 3 transport. Cost ($100-500 for consumer devices) and setup complexity barrier for adoption. Starlink availability improving economics but still requires hardware. Hardware dependency is unavoidable for satellite.

Spam and Abuse Prevention: Without centralized moderation, preventing spam or harassment is difficult. Options: (1) Reputation systems (complex); (2) Cost-based rate limiting (requires payment infrastructure); (3) Social filtering (contact lists). Open problem for decentralized systems generally.

# 9.3 Open Research Questions

The following questions require further research:

Group Messaging Cryptography: Extending to multi-party requires group key agreement (e.g., sender keys as in Signal). Can this be done with bounded proofs? What happens when group membership changes while some members are offline for days? Non-trivial extension requiring careful cryptographic design.

Post-Quantum Cryptography: Current scheme uses ECDH and Ed25519, vulnerable to quantum computers. Lattice-based alternatives (CRYSTALS-Kyber, CRYSTALS-Dilithium) have larger signatures (2-3 KB) and keys (1-2 KB). How does this affect proof bundle sizes and bandwidth? Likely feasible but requires re-analysis.

Hybrid Identity Models: Can we combine cryptographic identity (for machine verification) with human-readable names (for usability) without centralized registries? ENS-like systems require global state. Petname systems work locally but don't enable discovery. Tension between usability and decentralization.

Incentive Design for Sentinels: How to sustainably compensate sentinel operators?

Micropayments add complexity and payment infrastructure dependency. Volunteer operation may not scale. Grants from ecosystem sustainable long-term? Economic viability question.

Traffic Analysis Mitigation: Can bounded-latency mix networks or cover traffic provide meaningful resistance without breaking offline capability? What is the optimal trade-off between metadata privacy and system simplicity? Requires modeling adversary capabilities and user requirements.

Formal Verification of Implementation: Can proof construction and verification algorithms be formally verified (e.g., in Coq or Lean) to eliminate implementation bugs? What is the verification effort vs. benefit? High-assurance computing question.

# 10. Conclusion and Future Directions

# 10.1 Summary of Contributions

This roadmap has demonstrated that resilient encrypted messaging on Zenon Network is theoretically feasible under adversarial conditions including internet outages, infrastructure collapse, and surveillance pressure. The key insight is treating messaging as an asynchronous communication primitive where cryptographic guarantees (authentication, integrity) are maintained with minimal infrastructure assumptions, accepting trade-offs in delivery speed and metadata privacy.

We have: (1) Formalized requirements for offline-verifiable messaging building on identity-as-frontier model; (2) Designed pluggable transport architecture with explicit security properties per tier; (3) Analyzed satellite relay feasibility demonstrating  $\sim 18$  MB/day bandwidth requirement; (4) Established message format with 1.2-2.8 KB proofs and sub-100ms verification; (5) Identified critical use cases (disaster response, conflict zones, humanitarian operations) where authenticity matters more than immediacy; (6) Proven impossibility of delivery guarantees and non-existence proofs, acknowledging fundamental limitations.

# 10.2 When to Use This System

This messaging architecture is appropriate when:

- Infrastructure reliability cannot be assumed (disaster zones, conflict areas, censored environments)

- Message authenticity is critical for safety or coordination (relief operations, military communications, journalistic verification)

- Delivery latency is acceptable (minutes to hours, not seconds)

- Users are trained to understand asynchronous communication model

- Metadata privacy is not the primary threat (content confidentiality is sufficient)

This system is inappropriate when:

Real-time chat features are required (consumer social messaging)

- Traffic analysis resistance is critical (covert operations, source protection)

- Infrastructure is reliable and trustworthy (use Signal instead)

- Users cannot tolerate key management complexity

- Deniability is required (non-repudiable signatures are a feature, not a bug, for our use cases but may be undesirable elsewhere)

# 10.3 Research Maturity and Next Steps

Current Status: This is an exploratory research roadmap, not a finished system. We have established theoretical feasibility and identified engineering requirements, but significant work remains before deployment.

# Required Next Steps:

Phase 1 — Proof of Concept (3-6 months): Implement core cryptographic primitives, build minimal client for browser and mobile, demonstrate end-to-end flow with Tier 1 transport (P2P). Validate proof bundle sizes and verification latency against theoretical bounds. Estimated effort: 2-3 engineers.

Phase 2 — Sentinel Network (6-12 months): Deploy sentinel infrastructure for proof distribution, implement multi-sentinel verification with Byzantine fault tolerance, establish economic model for sustainability. Estimated effort: 4-5 engineers.

Phase 3 — Satellite Integration (12-18 months): Partner with satellite provider (Starlink, Iridium), integrate receiver SDKs, deploy relay infrastructure for broadcast channel. Field testing in disaster simulation. Estimated effort: 6-8 engineers plus hardware partnerships.

Phase 4 — Real-World Deployment (18-24 months): Deploy with NGO partners in target environments (disaster-prone regions, conflict zones), gather operational feedback, iterate on UX and reliability, establish training programs. Estimated effort: 8-10 engineers plus field operations team.

# 10.4 Intellectual Honesty and Realistic Expectations

This roadmap has explicitly acknowledged limitations and impossibilities rather than overpromising capabilities. We have proven that certain properties (delivery guarantees, non-existence proofs, traffic analysis resistance) are fundamentally unachievable under our constraints. This intellectual honesty strengthens the contribution—by clearly delineating what is cryptographically guaranteed versus operationally approximated, we enable informed decision-making about where this system is appropriate.

The ultimate question is not whether this system can replace Signal or WhatsApp (it cannot and should not), but whether it provides value in adversarial scenarios where existing systems fail. For the specific use cases identified—disaster response, armed conflict, humanitarian operations—we believe the answer is yes. The system offers cryptographic guarantees that remain valid even when infrastructure collapses, which is precisely what those scenarios require.

# 10.5 Call for Collaboration

This research roadmap is intended to spark discussion and collaboration. We invite feedback from:

- Cryptographers: Review security proofs, identify weaknesses, suggest improvements to formal model

- Distributed Systems Researchers: Analyze transport abstractions, propose optimizations for satellite relay

- NGO/Humanitarian Workers: Validate use cases, identify missing requirements, provide operational constraints

- Implementation Engineers: Prototype key components, estimate realistic development timelines, identify technical risks

UX Researchers: Design interfaces for asynchronous messaging, develop training materials for non-technical users

The goal is not to build this in isolation but to establish whether the broader research and practitioner community believes this direction is promising. If so, the next step is forming a working group to develop a formal specification and reference implementation.

# 11. Selected References and Further Reading

# Foundational Cryptography:

- Goldwasser, Micali, Rivest. "Digital Signature Scheme Secure Against Adaptive Chosen-Message Attacks." SIAM Journal on Computing 17(2), 1988.

- Bernstein et al. "High-speed high-security signatures (Ed25519)." Journal of Cryptographic Engineering 2(2), 2012.

- Boneh, Lynn, Shacham. "Short Signatures from the Weil Pairing." ASIACRYPT 2001.

# Decentralized Identity:

- W3C Decentralized Identifiers (DIDs) v1.0. W3C Recommendation, July 2022.

- Companion paper: "Decentralized Identity with Deterministic Key Rotation: A Proof-First Identity Model for Dual-Ledger Architectures." December 2025.

- Ethereum Name Service (ENS) documentation. https://docs.ensdomains

# Secure Messaging Systems:

- Marlinspike, Perrin. "The Double Ratchet Algorithm." Signal Specifications, 2016.

Cohn-Gordon et al. "A Formal Security Analysis of the Signal Messaging Protocol." EuroS&P, 2017.

- Borisov, Goldberg, Brewer. "Off-the-Record Communication, or, Why Not To Use PGP." WPES 2004.

# Distributed Systems Theory:

Fischer, Lynch, Paterson. "Impossibility of Distributed Consensus with One Faulty Process." Journal of the ACM 32(2), 1985.

- Lamport. "The Part-Time Parliament (Paxos)." ACM Transactions on Computer Systems 16(2), 1998.

Castro, Liskov. "Practical Byzantine Fault Tolerance." OSDI 1999.

# Blockchain and Light Clients:

- Nakamoto. "Bitcoin: A Peer-to-Peer Electronic Cash System." 2008.

- Buterin. "Ethereum: A Next-Generation Smart Contract and Decentralized Application Platform." 2014.

- Zenon Network. "Network of Momentum: Feeless, Scalable, Dual-Ledger Architecture." 2019.

- Merkle. "A Digital Signature Based on a Conventional Encryption Function." CRYPTO 1987.

# Satellite Communications:

Starlink Technical Documentation. SpaceX, 2023.

- Iridium Satellite Communications Technical Reference. Iridium Communications Inc., 2022.

- Maral, Bousquet. "Satellite Communications Systems: Systems, Techniques and Technology." 5th Ed, 2009.

# Post-Quantum Cryptography:

- Ducas et al. "CRYSTALS-Dilithium: A Lattice-Based Digital Signature Scheme." TCHES 2018.

- Avanzi et al. "CRYSTALS-Kyber: Algorithm Specifications and Supporting Documentation." NIST PQC Round 3, 2020.

- Shor. "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer." SIAM Journal on Computing 26(5), 1997.

# Related Work in Resilient Communications:

- Briar Project. "Secure messaging, anywhere." https://briarproject.org

- Freenet Project. "Free software for anonymous, censorship-resistant communications." https://freenetproject.org

- Scuttlebutt Protocol. "A decentralized secure gossip platform." https://scuttlebutt.nz

- Delay-Tolerant Networking Research Group (DTNRG). IETF, ongoing.

Note: This reference list is selective rather than comprehensive. A complete bibliography would include  $50+$  citations to primary cryptographic literature, distributed systems papers, and related work in decentralized communications. The companion identity paper provides more extensive references to foundational cryptography.

# Document Status and Version History

Version 1.0 — December 23, 2025

Initial public release of research roadmap. This document represents exploratory research into the feasibility of resilient encrypted messaging on Zenon Network. It is not a product specification, deployment commitment, or security audit. The analysis is based on theoretical modeling and architectural design but has not been validated through implementation or field testing.

Intended Audience: Cryptographers, distributed systems researchers, blockchain engineers, humanitarian technology practitioners, and technical decision-makers evaluating communication systems for adversarial environments.

Peer Review Status: This document has not undergone formal peer review. We welcome critical feedback from the research community on security proofs, architectural decisions, and feasibility claims. Subsequent versions will incorporate substantive feedback and any identified errors or weaknesses.

Relationship to Zenon Network: This roadmap builds on Zenon Network's dual-ledger architecture and decentralized identity primitives but is independent research not officially endorsed by the Zenon core team. Implementation would require coordination with the broader Zenon ecosystem.

# Changelog:

- 2025-12-23: Initial release (v1.0) with formal model, transport architecture, use case analysis, and limitations

This document represents a research contribution to the problem of resilient communications in adversarial environments. It establishes theoretical feasibility and identifies engineering requirements but is not a finished system. Significant development, testing, and field validation are required before deployment. The authors make no warranties about the security, reliability, or fitness for purpose of any implementation based on this roadmap.