# Browser Light Client (Draft Notes)

These are early notes on what a minimal Zenon light client inside a web browser might look like. This is not a spec, just an outline for thinking about the idea.

## Why a browser client makes sense

Some parts of the Zenon design line up well with modern browsers:

- dual-ledger structure (local state is small)
- deterministic zApp interfaces
- micro-PoW instead of gas
- simple header verification

Modern browsers can handle WASM and P2P transports.

## What a minimal client would do

A simple first version only needs to:

1. Connect to a peer (sentry or full node) using a browser-friendly transport.
2. Pull and verify recent Momentum headers.
3. Follow the user’s AccountChain and keep basic local state.
4. Build and sign transactions in the browser.
5. Generate micro-PoW in a worker thread.
6. Relay transactions through the connected peer.

## Rough session flow

1. Load the app → initialize crypto + WASM.
2. Connect to a peer using WebRTC/libp2p or a bridge.
3. Sync and verify Momentum headers.
4. Fetch AccountChain data for the user.
5. When sending a transaction:
   - build and sign locally  
   - generate micro-PoW  
   - submit through the peer  
6. Keep following headers until the tx is confirmed.

## Open questions

- How light can the proofs be?
- How much AccountChain data should be cached?
- What are realistic micro-PoW limits in browsers?
- How much help should sentries give browser clients?

These notes can be expanded later once the broader structure becomes clearer.
