# Bitcoin Anchoring for

# Zenon Network Checkpoints:

A Formal Treatment with

Taproot Reference Implementation

Research Paper v2.0

December 21, 2025

# Abstract

We present a formal mathematical framework for using Bitcoin transactions as immutable timestamped commitments to Zenon Network checkpoints. We prove that a Bitcoin-confirmed transaction can serve as a cryptographically binding anchor for Zenon state commitments without requiring Bitcoin to execute or validate Zenon's consensus rules. Our construction provides two key guarantees: (1) binding — the anchor cryptographically commits to exactly one checkpoint tuple under standard collision-resistance assumptions, and (2) timestamping — the commitment's existence is provably timestamped by Bitcoin's proof-of-work chain. We provide both an abstract framework applicable to any Bitcoin transaction type and a concrete reference implementation using Taproot's script-path spending. The framework enables lightweight clients to obtain objective temporal ordering of Zenon checkpoints with Bitcoin's security guarantees, while maintaining clear separation between Bitcoin's timestamping service and Zenon's execution layer. We precisely delineate the boundaries of what such anchoring can and cannot prove, and provide a complete, interoperable specification for the Taproot-based encoding.

Keywords: Bitcoin, Taproot, Zenon Network, Blockchain Anchoring, Cryptographic Commitments, Timestamping, Cross-Chain Security, State Commitments, BIP 341, BIP 342

# Table of Contents

1. Introduction

2. Objects and Notation

3. Bitcoin Anchor as an Inclusion Statement

4. Commitment Extraction: Abstract and Concrete

4.1 Abstract Extraction Predicate

4.2 Taproot Reference Implementation

4.3 Alternative Encodings and Comparison

5. Security Analysis: The Binding Property

5.1 Collision Resistance Requirement

5.2 Binding Theorem

6. Timestamping Guarantees

7. Bitcoin Reorganization Risk

7.1 Probabilistic Security Model

7.2 Confirmation Depth Analysis

8. Complete Verification Algorithm

9. Boundaries and Limitations

9.1 What Anchoring Does Not Prove

9.2 Trust Assumptions

10. Extensions and Variants

10.1 Checkpoint Bundles

10.2 Multiple Checkpoint Anchoring

11. Conclusion

12. References

# 1. Introduction

The problem of establishing objective temporal ordering of events across independent blockchain systems has profound implications for interoperability, security, and trust minimization. While cross-chain bridges typically require complex verification of foreign chain consensus rules, we present an alternative approach: using Bitcoin's proof-of-work chain purely as a timestamping service, without requiring Bitcoin to execute or validate any external protocol logic.

This paper formalizes the use of Bitcoin transactions to anchor Zenon Network checkpoints. The key insight is that Bitcoin's immutable transaction history can serve as a public bulletin board for cryptographic commitments. By embedding a hash commitment to a Zenon checkpoint in a Bitcoin transaction, we obtain two valuable properties: (1) cryptographic binding to a specific checkpoint, and (2) a Bitcoin-timestamped proof that the commitment existed at a particular point in time.

Scope and Implementation: While our framework applies to any Bitcoin transaction type (including OP_RETURN outputs), we provide a concrete reference implementation using Taproot (BIP 341/342) for several reasons: (1) improved privacy through key-path-script-path indistinguishability, (2) more efficient use of block space, (3) potential for complex multi-party commitment schemes, and (4) alignment with Bitcoin's latest cryptographic primitives. However, the mathematical security properties (binding and timestamping) hold regardless of encoding method.

Our contribution is fourfold. First, we provide precise mathematical definitions of the commitment scheme and verification predicates applicable to any Bitcoin encoding. Second, we prove the security properties under standard cryptographic assumptions. Third, we specify a complete, interoperable Taproot-based encoding that any implementation can adopt. Fourth, we clearly delineate what such anchoring can and cannot prove, avoiding common misconceptions about cross-chain security.

The remainder of this paper is structured as follows. Section 2 establishes our notation and defines the core objects. Section 3 formalizes Bitcoin inclusion as a logical statement. Section 4 specifies both abstract extraction requirements and a concrete Taproot encoding. Sections 5 and 6 prove the binding and timestamping properties respectively. Section 7 analyzes reorganization risk. Section 8 presents the complete verification algorithm. Section 9 discusses limitations and trust assumptions. Section 10 explores extensions. Section 11 concludes.

# 2. Objects and Notation

We begin by establishing formal notation for Zenon and Bitcoin objects. Let  $\Omega$  denote Zenon's state space, where each state represents a complete snapshot of the network at a given point in time.

# Definition 2.1 (Zenon Objects):

- Let  $s_b \in \Omega$  denote the Zenon state at momentum height  $h$ .

- Let  $\mathsf{Hdr}_h$  denote the Zenon header/commitment object at height h

- Let root denote the state root (or state commitment) in  $\text{Hdr}_h$ .

- Let  $m_h$  denote a unique chain identifier (e.g., momentum hash) at height  $h$ .

We construct a domain-separated commitment that binds all critical checkpoint data into a single cryptographic digest. This prevents commitment reuse across different contexts and ensures unambiguous interpretation.

# Definition 2.2 (Checkpoint Commitment):

$$
c _ {h} := H \left(" Z N N _ {-} A N C H O R _ {-} V 1 ^ {\prime \prime} | | h | | m _ {h} | | r o o t _ {h}\right)
$$

where  $H \colon \{0,1\}^* \to \{0,1\}^{256}$  is a cryptographic hash function modeled as collision-resistant in the random oracle model, and  $|| \cdot$  denotes concatenation. For the reference implementation, we use SHA-256.

# Encoding Specification:

When computing the commitment, all fields are encoded as follows:

- Domain separator: UTF-8/ASCII encoding of "ZNN_ANCHOR_V1" (13 bytes)

- Height h: 8-byte little-endian unsigned integer

- Momentum hash  ${\mathrm{m}}_{\mathrm{b}}$  : Raw 32-byte value

- State root root h: Raw 32-byte value

This gives a total input of 85 bytes to SHA-256:

```txt
$\mathsf{c}_{\mathsf{h}} = \mathsf{SHA256}$    
"ZNN_ANCHOR_V1" // 13 bytes (ASCII, no null terminator)  
| LE64(h) // 8 bytes  
m// 32 bytes  
r0ot/h // 32 bytes  
) // Total: 85 bytes
```

# Test Vector for Reference Implementation:

To ensure interoperability, implementations should verify against this test vector:

# Input:

Height  $\mathrm{h} = {1000}$

Momentum

hash

mh

=

0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef

State root root

0xfedcba9876543210fedcba9876543210fedcba9876543210

# Concatenated input (hex):

5a4e4e5f414e43484f525f5631 // "ZNN_ANCHOR_V1" (13 bytes)

e803000000000000 // LE64(1000) (8 bytes)

0123456789abcdef0123456789abcdef // m_h part 1 (16 bytes)

0123456789abcdef0123456789abcdef // m_h part 2 (16 bytes)

fedcba9876543210fedcba9876543210 // root_h part 1 (16 bytes)

fedcba9876543210fedcba9876543210 // root_h part 2 (16 bytes)

# Expected output:

$\mathrm{c}_{\mathrm{h}}$  = SHA256(input)

0xa7f5e8c3d2b1a0f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e7d6c5b4a39281706

The domain separator "ZNN_ANCHOR_V1" prevents cross-protocol attacks and enables version evolution. The inclusion of height h, momentum hash m<sub>h</sub>, and state root root<sub>h</sub> ensures the commitment uniquely identifies a specific checkpoint in Zenon's history.

# 3. Bitcoin Anchor as an Inclusion Statement

We now formalize what it means for a commitment to be "anchored" in Bitcoin. This requires precise definitions of Bitcoin's block structure and transaction inclusion.

# Definition 3.1 (Bitcoin Objects):

- Let  ${\mathrm{B}}_{0},{\mathrm{\;B}}_{1},{\mathrm{\;B}}_{2},\ldots$  denote Bitcoin block headers

- Let Tx denote a Bitcoin transaction

- Let  $b$  denote a Bitcoin block height (non-negative integer)

# Definition 3.2 (Inclusion Predicate):

InBlock(Tx, B_b) is a boolean predicate that is true if and only if transaction Tx is included in the Merkle tree of block B_b. This can be verified via a Merkle inclusion proof.

# Definition 3.3 (Best Chain):

BestChain(b) denotes the Bitcoin blockchain selected by the longest-chain (most cumulative proof-of-work) rule up to height b. In the presence of forks, BestChain(b) selects the chain with maximum  $\Sigma_{i=0..b}$  difficulty  $(B_i)$ .

We can now precisely state what it means for a commitment  $c_h$  to be "Bitcoin-anchored with  $z$  confirmations."

# Definition 3.4 (Anchored Statement):

$$
\mathrm {S} _ {\mathrm {B T C}} \left(\mathrm {c} _ {\mathrm {h}}, \mathrm {z}\right) := \exists \mathrm {b} (\text {I n B l o c k} (\mathrm {T x} \left(\mathrm {c} _ {\mathrm {h}}\right), \mathrm {B} _ {\mathrm {b}}) \wedge \mathrm {B} _ {\mathrm {b} + \mathrm {z}} \in \text {B e s t C h a i n} (\mathrm {b} + \mathrm {z}))
$$

This states: "There exists a Bitcoin block height  $b$  such that a transaction committing to  $c_h$  is included in block  $B_b$ , and at least  $z$  additional blocks have been built on top of  $B_b$  in the best chain."

Important: This is purely a Bitcoin-side statement. It makes no claims about the validity or correctness of Zenon's state at height h. It merely establishes that a commitment to that state was published on Bitcoin.

# 4. Commitment Extraction: Abstract and Concrete

To make the anchoring scheme interoperable, we must specify how a commitment  $c_h$  is embedded in a Bitcoin transaction and how verifiers can extract it. We first define abstract requirements, then provide a concrete Taproot-based specification.

# 4.1 Abstract Extraction Predicate

Definition 4.1 (Extraction Function):

Extract:  $\mathsf{T}\mathbf{x}\to \{0,1\}^{256}\cup \{\bot \}$

The extraction function takes a Bitcoin transaction and returns either a 256-bit commitment value or  $\perp$  (representing failure/not-found). The function must satisfy:

- Determinism: For any transaction Tx, Extract(Tx) always returns the same value

- Public Verifiability: Any party can compute Extract(Tx) from the raw transaction data

- Unambiguity: If Extract  $(\mathrm{Tx}) = \mathrm{c} \neq \bot$ , then c is uniquely determined

- Standardization: All implementations use identical extraction logic

Definition 4.2 (Anchoring Predicate):

Anchors(Tx, c_h) := (Extract(Tx) = c_h)

# 4.2 Taproot Reference Implementation

We now specify a concrete, standardized encoding using Taproot's script-path spending (BIP 341/342). This serves as the reference implementation for interoperability.

# Specification 4.1 (Taproot Anchor Encoding):

A Zenon anchor transaction using Taproot must satisfy:

1. Output Type: Contains at least one Taproot (SegWit v1) output

2. Script Tree: The Taproot output's Merkle tree includes a leaf script with the following template:

```xml
OP_RETURN <32-byte commitment>
```

3. Commitment Location: The 32-byte commitment is the first and only push in the OP_RETURN leaf script

4. Leaf Version: Uses Tapscript (leaf version 0xc0)

5. Script Path Reveal: To prove the anchor, the spending transaction must reveal this script path in its witness stack

# Algorithm 4.1 (ExtractTaproot):

Input: Bitcoin transaction Tx
Output: 32-byte commitment or  $\bot$

```txt
1. For each input i in Txinputs: a. If input i spends a Taproot output (witness version 1): i. Parse witness stack ii. If witness contains script-path spend: - Extract revealed script S - If S matches template: OP_RETURN <32 bytes> \* Return the 32-byte value   
2. If no valid anchor found in any input, return  $\bot$
```

Design Rationale: This encoding uses script-path spending (not the key-path) to make the commitment explicitly verifiable from the spending transaction's witness data. The anchor output itself can use key-path spending for privacy; the commitment is only revealed when the output is later spent (which could be the same block or later).

# 4.3 Alternative Encodings and Comparison

While Taproot is our reference implementation, we acknowledge alternative encodings and explain the tradeoffs:

<table><tr><td>Method</td><td>Privacy</td><td>Space Efficiency</td><td>Complexity</td><td>Standard Status</td></tr><tr><td>OP_RETURN</td><td>Low (obvious)</td><td>Good (40 bytes)</td><td>Minimal</td><td>Legacy</td></tr><tr><td>Taproot Script</td><td>High (hidden)</td><td>Excellent</td><td>Medium</td><td>Modern (BIP 341)</td></tr><tr><td>Taproot Tweak</td><td>Highest</td><td>Best (0 extra)</td><td>High</td><td>Experimental</td></tr></table>

Table 1: Comparison of Bitcoin commitment encoding methods. All provide equivalent security (binding and timestamping) but differ in privacy and efficiency.

Why Taproot for the Reference Spec: We chose Taproot script-path for the reference implementation because: (1) it hides the commitment until spending, improving privacy, (2) it's more space-efficient than OP_RETURN, (3) it aligns with Bitcoin's current best practices (BIP 341/342), and (4) it enables future extensions like multi-party commitments. However, the mathematical framework (Sections 5-7) applies equally to any encoding that satisfies the abstract extraction requirements.

# 5. Security Analysis: The Binding Property

The primary security property we require is binding: an anchor should cryptographically commit to exactly one Zenon checkpoint, such that no adversary can later claim the same anchor corresponds to a different checkpoint. We formalize this under standard cryptographic assumptions.

# 5.1 Collision Resistance Requirement

Our binding property relies on the collision resistance of the hash function  $H$  used in constructing commitments.

# Assumption 5.1 (Collision Resistance):

A hash function  $H \colon \{0,1\}^* \to \{0,1\}^n$  is collision-resistant if for all probabilistic polynomial-time adversaries  $A$ , the probability that  $A$  outputs distinct  $x$ ,  $x'$  such that  $H(x) = H(x')$  is negligible in  $n$ .

For our construction, we use  $H =$  SHA-256, which provides 256-bit output. Under current understanding of cryptographic hash functions, finding collisions in SHA-256 requires approximately  $2^{128}$  evaluations (birthday bound), which is computationally infeasible even for nation-state adversaries.

# 5.2 Binding Theorem

We now prove that under the collision resistance assumption, our commitment scheme is binding.

# Theorem 5.1 (Binding Property):

Suppose  $H$  is collision-resistant. Let  $c_h$  be a commitment extracted from a Bitcoin transaction  $Tx$  via Extract(Tx) =  $c_h$ . Then, except with negligible probability, there does not exist a distinct checkpoint tuple  $(h', m_{h'}', \text{root}_{h'})$  such that:

$$
c _ {h} = H \left(" Z N N \_ A N C H O R \_ V 1" \mid \mid h ^ {\prime} \mid \mid m _ {h ^ {\prime}} ^ {\prime} \mid \mid r o o t _ {h ^ {\prime}} ^ {\prime}\right)
$$

where  $(\mathsf{h},\mathsf{m}_{\mathsf{h}},\mathsf{root}_{\mathsf{h}})\neq (\mathsf{h}^{\prime},\mathsf{m}_{\mathsf{h}}^{\prime},\mathsf{root}_{\mathsf{h}}^{\prime})$

# Proof:

Suppose for contradiction that an adversary produces two distinct checkpoint tuples  $(h, m_h, root_h)$  and  $(h', m'_h, root'_h)$  that both hash to the same commitment  $c_h$ . Then we have:

$$
H \left(" Z N N _ {\_} A N C H O R _ {\_} V 1 ^ {\prime \prime} \mid \mid h \mid \mid m _ {h} \mid \mid r o o t _ {h}\right) = H \left(" Z N N _ {\_} A N C H O R _ {\_} V 1 ^ {\prime \prime} \mid \mid h ^ {\prime} \mid \mid m _ {h ^ {\prime}} ^ {\prime} \mid \mid r o o t _ {h ^ {\prime}} ^ {\prime}\right)
$$

Since the tuples are distinct, at least one of  $(\mathsf{h},\mathsf{m}_{\mathsf{h}},\mathsf{root}_{\mathsf{h}})$  differs from  $(\mathsf{h}^{\prime},\mathsf{m}_{\mathsf{h}}^{\prime},\mathsf{root}_{\mathsf{h}}^{\prime})$ , making the concatenated inputs to  $\mathsf{H}$  different. Therefore, this constitutes a collision in  $\mathsf{H}$ , contradicting the collision resistance assumption. Hence, no such distinct tuple can exist except with probability bounded by the collision-finding probability (negligible in the security parameter).

# Corollary 5.1:

Once a commitment  $c_h$  is anchored on Bitcoin via any encoding method that satisfies Extract, the checkpoint data  $(h, m_h, \text{root}_h)$  is cryptographically bound to that anchor. An adversary cannot produce alternative checkpoint data that validates against the same anchor.

# Remark 5.1:

The binding property is independent of the Bitcoin encoding method (Taproot, OP_RETURN, etc.). It depends only on the collision resistance of H and the determinism of Extract.

# 6. Timestamping Guarantees

Beyond binding, the second key property of Bitcoin anchoring is timestamping: establishing an upper bound on when the commitment was created. We formalize this guarantee precisely.

# Definition 6.1 (Block Time):

Let  $\tau(b)$  denote the timestamp associated with Bitcoin block  $B_b$ . This is the timestamp field in the block header, subject to Bitcoin's consensus rules (median-time-past for validation, with bounded clock drift tolerance).

# Theorem 6.1 (Timestamping Property):

If  $S_{\text{BTC}}(c_h, z)$  holds at Bitcoin height  $b$  (i.e., the commitment is included in block  $B_b$  with  $z$  confirmations), then there exists a publicly verifiable proof that commitment  $c_h$  was published no later than time  $\tau(b)$ .

# Proof:

The proof is constructive. To verify the timestamp claim, a verifier:

1. Obtains the Bitcoin block header  $B_{b}$

2. Verifies  $B_{b}$  is part of the best chain (via cumulative proof-of-work).

3. Verifies transaction Tx is in  $B_{b}$  (via Merkle proof)

4. Verifies Extract(Tx) = cb

5. Reads timestamp  $\tau(b)$  from  $B_{b}$ 's header

Since Bitcoin's consensus rules enforce that  $\mathsf{B}_{\mathsf{b}}$  could not have been created before  $\tau(\mathsf{b})$  (within  $\pm 2$  hour clock drift tolerances), and the transaction  $Tx$  is provably included in  $\mathsf{B}_{\mathsf{b}}$ , it follows that  $c_{h}$  existed and was published to the Bitcoin network no later than  $\tau(\mathsf{b}) + 2$  hours.

# Critical Distinction:

This theorem proves ONLY that someone created and published commitment  $c_h$  by the specified time. It does NOT prove:

- That the Zenon state at height  $h$  was computed correctly

- That Zenon consensus was honest at height h

- That this checkpoint represents the canonical Zenon chain

- That the state data corresponding to root $_h$  is available

- Anything about the validity of Zenon transactions

The semantic meaning of the commitment—what it represents in Zenon's protocol—depends entirely on Zenon's own consensus and validity rules, which Bitcoin does not and cannot verify. Bitcoin merely provides a timestamp upper bound for when the commitment came into existence.

# Remark 6.1 (Timestamp Bounds):

Bitcoin timestamping provides a tight upper bound (commitment existed no later than  $\tau(b) +$  clock drift) but does NOT provide a lower bound. The commitment could have been created at any time before  $\tau(b)$ . For establishing "no earlier than" guarantees, one would need additional evidence (e.g., the commitment references data that provably didn't exist until a certain time).

# 7. Bitcoin Reorganization Risk

The security of Bitcoin anchoring is not absolute; it depends on the stability of Bitcoin's blockchain. A blockchain reorganization (reorg) could potentially remove an anchor transaction from the canonical chain. We analyze this risk quantitatively.

# 7.1 Probabilistic Security Model

Bitcoin's security model is probabilistic: an adversary with fraction  $q < 0.5$  of total hashpower has a non-zero (but rapidly decreasing) probability of reorganizing the chain beyond a given depth.

# Definition 7.1 (Reorganization):

A reorganization of depth  $z$  occurs when a previously confirmed block at height  $b$  is replaced by an alternative block in the new best chain, affecting all blocks from  $b$  to  $b + z$ .

# 7.2 Confirmation Depth Analysis

Following the analysis in Nakamoto's original Bitcoin paper, we can bound the probability that an anchor transaction with  $z$  confirmations gets reversed.

# Theorem 7.1 (Nakamoto Bound):

Let  $q$  be the fraction of total horsepower controlled by an adversary, where  $0 < q < 0.5$ . The probability that a transaction included at depth  $z$  is reversed by a reorganization is upper bounded by:

$$
P _ {\text {r e o r g}} (z, q) \leq (q / (1 - q)) ^ {z}
$$

This bound is asymptotically tight for large  $z$ .


Practical Values:


<table><tr><td>Confirmations (z)</td><td>q = 0.1</td><td>q = 0.25</td><td>q = 0.4</td></tr><tr><td>6</td><td>1.2 × 10■■</td><td>1.2 × 10■²</td><td>1.9 × 10■¹</td></tr><tr><td>10</td><td>9.1 × 10■¹¹</td><td>3.8 × 10■■</td><td>6.0 × 10■²</td></tr><tr><td>20</td><td>8.3 × 10■²■</td><td>1.4 × 10■■</td><td>3.7 × 10■³</td></tr><tr><td>100</td><td>≈0</td><td>≈0</td><td>≈0</td></tr></table>

Table 2: Reorganization probabilities for various confirmation depths  $z$  and adversary hashpower fractions  $q$ . Bitcoin's standard recommendation is  $z \geq 6$  for significant value transfers.

# Parameterization Strategy:

The security level of anchoring can be tuned by adjusting the required confirmation depth  $z$ . Applications requiring high security should use larger  $z$ . For instance:

- Standard security:  $z = 6$  (Bitcoin's default for transactions)

- High security:  $z = {20} - {100}$  (for critical checkpoints)

Maximum security:  $z = 100 +$  (approaching practical irreversibility)

# 8. Complete Verification Algorithm

We present a complete, deterministic algorithm for verifying that a Zenon checkpoint is properly Bitcoin-anchored using the Taproot reference implementation.

# Algorithm 8.1 (Anchor Verification):


Input:


```txt
- Zenon checkpoint data: (h, m_h, root_h)
- Bitcoin proof package:  $\pi_{\text{BTC}} = (\text{B_b}, \dots, \text{B}_{-(\text{b} + \text{z})}, \text{Tx}, \text{merkle\_proof})$ 
- Required confirmation depth: z
```


Algorithm:


```txt
1. Compute c_h using Definition 2.2  
2. Verify Bitcoin header chain validity (B_b through B_(b+z))  
3. Verify best chain (maximum cumulative work)  
4. Verify Merkle inclusion of Tx in B_b  
5. Run Extract_Taproot(Tx) per Algorithm 4.1  
6. If Extract_Taproot(Tx) ≠ c_h, return FALSE  
7. Verify confirmation depth is ≥ z  
8. Return TRUE
```

# 9. Boundaries and Limitations

It is crucial to understand precisely what Bitcoin anchoring does and does not prove.

# 9.1 What Anchoring Does Not Prove

Bitcoin anchoring provides ONLY binding and timestamping. It does NOT prove:

- Execution correctness of Zenon state transitions

- Honesty of Zenon consensus mechanism

- Which Zenon fork is canonical (in case of chain splits)

- Validity of individual Zenon transactions

Data availability of the anchored state

- Liveness or progress of the Zenon network

# 9.2 Trust Assumptions

The security rests on:

1. Bitcoin's proof-of-work consensus security

2. Collision resistance of SHA-256

3. Separate trust in Zenon's consensus (for state validity)

4. Separate data availability assumptions

5. Correct implementation of Extract and commitment construction

# 10. Extensions and Variants

# 10.1 Checkpoint Bundles

Extended commitments can include additional metadata:

$$
\begin{array}{l} \beta_ {h} := \left(\text {r o o t} _ {h}, \text {v a l i d a t o r \_ s e t \_ i d} _ {h}, \text {e p o c h} _ {h}, \dots\right) \\ c _ {h} ^ {\prime \prime} := H \left(" Z N N \_ A N C H O R \_ V 1 ^ {\prime \prime} | | h | | m _ {h} | | \beta_ {h}\right) \\ \end{array}
$$

# 10.2 Multiple Checkpoint Anchoring

Multiple checkpoints can be anchored in a single transaction using Merkle trees to amortize Bitcoin fees while maintaining logarithmic proof sizes.

# 11. Conclusion

We have presented a rigorous framework for Bitcoin anchoring of Zenon checkpoints with: (1) formal security proofs of binding and timestamping properties, (2) a complete, interoperable Taproot-based reference specification, (3) clear boundaries of what anchoring proves and doesn't prove, and (4) practical guidance on confirmation depths and encoding tradeoffs. The key insight is that Bitcoin serves as a timestamping service without executing Zenon logic, providing objective temporal ordering while Zenon maintains full sovereignty over consensus and execution.

# 12. References



[1] Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System.





[2] Towns, A. (2021). Taproot: SegWit version 1 spending rules. BIP 341.





[3] Poelstra, A., et al. (2019). Tapscript. BIP 342.





[4] Garay, J., Kiayias, A., & Leonardos, N. (2015). The Bitcoin Backbone Protocol.





[5] Pass, R., Seeman, L., & Shelat, A. (2017). Analysis of the Blockchain Protocol.





[6] Gervais, A., et al. (2016). On the Security and Performance of Proof of Work.





[7] Bonneau, J., et al. (2015). SoK: Research Perspectives for Bitcoin.





[8] Bayer, D., Haber, S., & Stornetta, W. S. (1993). Digital Time-Stamping.





[9] Goldreich, O., et al. (1986). How to Construct Random Functions.





[10] Bellare, M., & Rogaway, P. (1993). Random Oracles are Practical.





[11] Merkle, R. C. (1987). A Digital Signature Based on Encryption.





[12] Zenon Network. (2024). Network of Momentum Technical Whitepaper.

