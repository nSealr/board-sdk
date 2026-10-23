# Linux host stream diagnostic

This standalone non-Nostr consumer runs four finite experiments through
`embedded-io 0.7.1` and real Linux Unix sockets. It demonstrates a byte-stream
integration decision for B01. It provides no Board driver or exported SDK API.
The [reviewed contract](../../docs/restart/B01/host-stream-probe-contract.md) and
[scope admission](../../docs/restart/B01/host-stream-probe-acceptance.json) fix
the oracle before implementation; the [execution record](../../docs/restart/B01/host-stream-probe/README.md)
preserves source identities, commands, environment and raw results.

Use Linux `x86_64-unknown-linux-gnu`, rustup and GNU `timeout`. Rust/Cargo 1.95.0
is pinned by the local `rust-toolchain.toml`; no Signer, hardware repository or
sibling checkout is needed. From this directory:

```sh
rustup toolchain install 1.95.0 --profile minimal --component rustfmt --component clippy
export RUSTUP_TOOLCHAIN=1.95.0
export CARGO_TARGET_DIR=/tmp/nsealr-host-stream-diagnostic-target
cargo fmt -- --check
cargo clippy --locked --all-targets --target x86_64-unknown-linux-gnu -- -D warnings
cargo build --locked --release --target x86_64-unknown-linux-gnu
timeout --signal=TERM --kill-after=2s 30s "$CARGO_TARGET_DIR/x86_64-unknown-linux-gnu/release/host-stream-diagnostic"
```

Build before starting the 30 s runtime watchdog. The binary accepts no arguments
and always executes all four cases. Every case uses a new connected socket pair;
both endpoints acknowledge startup before I/O. The peer uses `std::io` directly
and checks literal `B01PING\n`; the trait consumer accepts only `B01PONG\n`.

| Case | Required result |
| --- | --- |
| Response | Complete eight-byte response, peer EOF, both endpoints closed and both threads joined before publication. |
| Timeout | Silent connected peer; 100 ms configured read timeout yields raw `WouldBlock`, upstream `Other`, and no response. |
| Local cancel | Peer sends only `B01`; the controller waits for three bytes actually consumed, shuts down a cloned handle, then requires a zero-byte read and `UnexpectedEof`. A timeout fails this case. |
| Partial peer EOF | Peer sends `B01` and closes its write half; consumer reports `UnexpectedEof` and publishes no response. |

Other I/O has a 1 s timeout; control waits are 3 s. The trace records actual read
counts/errors and elapsed times. All cases require peer EOF, shutdown, dropped
handles and actual joins. A failure aborts with a nonzero exit status. A stuck
worker remains unavailable until collection; an external watchdog kill is a
failed experiment. No failed socket, response prefix or request is replayed.

`Cargo.lock` resolves the sole dependency to the exact registry archive checksum;
`std` enables upstream `alloc`, while `defmt` remains disabled. The dependency is
`MIT OR Apache-2.0` and its package includes both full license notices. No upstream
code is copied into this consumer. `publish = false` prevents accidental registry
publication. A socket `flush` is not a peer acknowledgment, and a read timeout is
per I/O call, not a generic total-operation deadline.

The host timings and shutdown behavior do not qualify a firmware deadline,
hardware cancellation, an electrical interface, entropy, key custody, human
consent, owner reset/recovery or a release. There is no hostile-application
isolation. All B01/B02/B03 criteria remain open; physical Board examples and
independent release qualification retain their own gates.
