# B01 proposed host stream consumer scope

Proposed 2026-10-23 by `/root/sdk_dependency_probe`, based on SDK main
`9ad3634dff5eeb3d578cfb7afc3a7680abcaa12a` (tree
`982a2bda037f30707f2d41ca6e3746fa273f9128`) and the B01 record in
`nSealr/nsealr@bd892b70b88aeaf72b10ad5e9152bc36674513b9`.
**Awaiting distinct scope review and coordinator admission; no executable scope
is granted by this proposal.** The existing [brief](brief.md), SDK-05, and
[documentary acceptance](documentary-acceptance.json) require that admission
before a crate or dependency is selected. Existing historical receipts remain
unchanged. All four B01 criteria remain open.

## One useful result and its owner

The assigned owner will produce one independently buildable, non-Nostr Linux
stream diagnostic consumer using an actual upstream byte-stream interface and
real kernel Unix sockets. It will establish whether the proposed generic stream
boundary can carry a fixed request/response and discard an incomplete operation
after timeout, local cancellation or peer closure. It supplies the first concrete
consumer for this interface decision; it does not stand in for a Board driver.

The consumer uses `embedded_io::{ErrorType, Read, Write}` with a small private
wrapper around `std::os::unix::net::UnixStream`. A second socket endpoint uses
`std::io` directly as the fixture peer. It checks literal bytes independently of
the consumer implementation; no success-returning stub, simulated peripheral,
new exported SDK API, executor, service or universal HAL is introduced. Each
operation owns its connection and fixed eight-byte response buffer. Only a
complete expected response is published. A failed connection is closed and is
never retried or reused; a later operation requires a new socket pair.

## Fixed sources and inputs, checked before implementation

Only `embedded-io = "=0.7.1"`, `default-features = false`, `features = ["std"]`
is proposed. The existing [source register](source-register.json) binds the
[official archive](https://static.crates.io/crates/embedded-io/embedded-io-0.7.1.crate):
SHA256 `9eb1aa714776b75c7e67e1da744b81a129b3ff919c8712b5e1b32252c1f07cc7`,
16,035 bytes; upstream revision
`21e547acd5c8fc7b26d9794f88c291dde912a788`, path `embedded-io`.
The original cached archive and these members were checked again without
installing a dependency:

- `src/lib.rs`: SHA256
  `1077dd3ed8cc4c44d2da1ef5b1e6f4322191b3e25c12407ace75df55b9083963`.
- `Cargo.toml`: SHA256
  `6f021b6c3db0f1e47398e7ff99a9e1852ac96b9dcdd0fd9219095568e725d09a`.

The published manifest sets MSRV 1.81, licenses `MIT OR Apache-2.0`, and makes
`std` enable `alloc`. `defmt` is optional and will remain disabled. Source
`src/lib.rs:202-222,299-354,373-417` provides the `std::io::Error` integration,
shared error type and blocking read/write contracts. There is no upstream
UnixStream implementation in this archive; the private wrapper is necessary.
It forwards actual I/O and errors, converts a zero-length result from a nonempty
write into `WriteZero`, and does not present socket flush as peer completion.
`read_exact` can consume a prefix before error; the enclosing consumer must
discard it. No common trait-level deadline or cancellation guarantee is assumed.

Host input is `x86_64-unknown-linux-gnu`, Rust/Cargo **1.95.0**, matching the
existing R00 toolchain pin, with no SDK baseline upgrade. `rustc +1.95.0 -Vv`
identifies compiler commit `59807616e1fa2540724bfbac14d7976d7e4a3860`; Cargo is
`1.95.0 (f2d3ce0bd 2026-03-21)`. This installed toolchain has no documentation
component. Its [exact upstream standard-library source](https://raw.githubusercontent.com/rust-lang/rust/59807616e1fa2540724bfbac14d7976d7e4a3860/library/std/src/os/unix/net/stream.rs)
was fetched and inspected instead: SHA256
`aaeb8a11bc9ad71cca92fe33717795198beb58b0ccd27544482605fb8b678dcd`,
23,983 bytes. Lines 158-203,270-310,460-483 specify
`UnixStream::{pair,try_clone,set_read_timeout,shutdown}`: connected sockets,
shared stream/options and shutdown of pending/future I/O. Lines 690-692 show
the socket `flush` implementation returning `Ok(())` without a peer acknowledgment.
The preliminary 1.96.1 documentation survey is superseded for this proposed
probe; it is not used as 1.95.0 evidence. No consumer was compiled or executed.

## First smoke, before final packaging

The public fixture request is the literal eight bytes `B01PING\n`; the complete
expected response is `B01PONG\n`. Prefix-only cases send exactly `B01`. The peer
checks the complete request before acting, and the consumer checks the complete
response before publishing it. Sockets are explicitly blocking. Read/write
timeouts are configured and read back, with a 100 ms read timeout for the silence
case and a 1 s fallback for other I/O. These values are host experiment inputs,
not selected firmware timing requirements. Record elapsed times and raw errors.
The Linux [`SO_RCVTIMEO` contract](https://man7.org/linux/man-pages/man7/socket.7.html)
(man-pages 6.19, 2026-06-05) gives `EAGAIN`/`EWOULDBLOCK` after a receive timeout
with no data transferred. Expect raw `std::io::ErrorKind::WouldBlock` and
`embedded_io::ErrorKind::Other`; do not normalize either into `TimedOut`.

| Case | Independent observable expectation |
| --- | --- |
| Start, request and response | Both endpoints report ready after socket configuration, before request I/O; the peer receives exactly `B01PING\n`, the consumer publishes exactly `B01PONG\n`, and both endpoint threads are joined after closure. |
| Timeout | After receiving the request the peer remains connected and silent. The configured blocking read fails with raw `WouldBlock` and upstream kind `Other`; no response is published, the connection is closed, and the peer observes EOF. |
| Cancel after partial input | The peer sends `B01` and withholds the suffix. A read-completion notification proves that the consumer has consumed exactly that prefix; only then the controller calls `shutdown(Both)` on its clone. A subsequent read returns zero and the worker reports `ReadExactError::UnexpectedEof`, with no response published. A timeout instead is a failed cancellation. All handles are dropped and both threads are joined. This proves local socket shutdown cancellation, not future-drop or hardware cancellation. |
| Peer close after partial input | The peer sends `B01` then closes its write half. The consumer reports incomplete EOF, publishes no response and closes. The peer observes EOF and is joined. |

Use bounded control-channel waits (3 s) and an external 30 s process watchdog.
Any failed assertion, control wait, join, watchdog kill or unexpected successful
partial response is a failed smoke and stays in the record. A controller request
or dropped thread handle is insufficient closure evidence. No retry, warm-up,
sleep-based readiness or reconstruction of a successful response is permitted.
Until actual worker collection, retain the response buffer/connection as owned
and unavailable; an uncollected worker is an uncertain/quarantined outcome, never
a successful cancellation or permission to reuse the buffer/socket.
The watchdog bounds the experiment, not the kernel or an eventual device driver.

## Admitted paths only after review, finish and limits

The proposed writable implementation perimeter is one package under
`examples/host-stream-diagnostic/` (`Cargo.toml`, `Cargo.lock`,
`rust-toolchain.toml`, `src/main.rs`, `README.md`) and its source-bound result under
`docs/restart/B01/host-stream-probe/`. No other package, dependency, driver,
hardware/Pi source, task graph or release status changes belong to this work.

Run the smoke first on the implementation, then build and execute the same
locked package from a clean standalone export without sibling checkouts. Capture
the complete commands, toolchain/kernel, dependency/features/lock resolution,
source and executable hashes, raw output, exit codes and any failures. Keep the
upstream full license notices available through the selected registry package;
copy no upstream implementation or manual body into this repository.

The owner finishes when these four cases pass on the exact candidate, standalone
resolution contains no Nostr/sibling/path dependency, and a distinct reviewer
checks the source against this previously frozen oracle and replays the smoke.
This is limited evidence for host stream integration and operation settlement.
It selects no MCU, SE, electrical tuple or physical device; proves no entropy,
custody, consent, reset/owner lifecycle, hard deadline, firmware isolation or
Board support; and closes no B01/B02/B03 or physical/release criterion. If this
scope is not admitted, stop with this concrete proposal and its exact missing
input: distinct scope acceptance plus coordinator admission.
