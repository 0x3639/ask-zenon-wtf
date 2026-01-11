# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **documentation-only repository** containing technical research papers, specifications, and architectural documents for **Zenon: The Network of Momentum (NoM)**—a distributed ledger protocol based on proof-of-momentum consensus.

There is no source code, build system, or testing infrastructure. All files are Markdown documentation.

## Document Hierarchy

**Core Team Papers (Normative):**
- `1_ZENON_LIGHTPAPER_(CORE_TEAM).md` - Original 2018 lightpaper
- `2_ZENON_WHITEPAPER_(CORE_TEAM).md` - Core whitepaper

**Greenpaper Series (Community-authored, Non-normative):**
- `ZENON_GREENPAPER.md` - Main verification-first architecture paper
- `0x00_greenpaper_series_bounded_verification.md` through `0x10_*.md` - Extended topics

**Architecture Documents:**
- `architecture-overview.md` - High-level system overview
- `node-architecture.md` - Node roles (Pillars, Sentinels, Supervisors, Sentries)
- `pillars.md`, `sentinel-*.md`, `supervisor-layer.md` - Layer specifications

**Research Topics:**
- Bitcoin SPV integration: `bitcoin-*.md`, `spv-*.md` files
- Light clients: `light-clients-verification.md`, `browser-light-client-*.md`
- Applications: `01_decentralized_identity_final.md`, `02_encrypted_messenger_research.md`
- State management: `minimal_state_frontier_*.md`, `state-proof-bundles.md`

## Key Concepts

**Dual-Ledger Architecture:**
- Account-chain layer: parallel, asynchronous execution per address
- Momentum chain layer: global sequential ordering via cryptographic commitments

**Core Innovations:**
- Bounded Verification: verification under explicit resource constraints (storage, bandwidth, computation)
- Proof-Native Applications (zApps): correctness via cryptographic proofs, not execution replay
- Composable External Verification (CEV): trustless validation of external facts (e.g., Bitcoin SPV)
- Application Contract Interfaces (ACIs): deterministic, schema-defined interfaces instead of general-purpose VMs

**Node Roles:**
- Pillars: consensus/finality layer, sign momentums
- Sentinels: verification and filtering layer
- Sentries: execution and proof-serving layer
- Supervisors: aggregation and coordination layer

## Document Status Markers

Many documents include status markers indicating their authority level:
- "Community-authored greenpaper (non-normative, non-official)"
- "Research Draft — Not a Formal Specification"
- "Pre-prototype draft"

## Working with This Repository

When asked about Zenon concepts, cross-reference multiple documents as topics often span several files. The greenpaper series (`0x00` through `0x10`) builds progressively on bounded verification concepts.
