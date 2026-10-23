# Distinct review: real host stream consumer

**PASS for the scoped Linux host experiment only; findings: none.** Reviewed
candidate `a14c0391457c6291899f650caef308b3694b44e8`, tree
`eff7e17253e20030cd33fd771d58dbbfc8104980`, against the frozen749860 contract and
distinct root admission `e3cdc8238a1012dca5ae4f5d80f70e35e56998a2` before running
the consumer. Reviewer `/root/a02_resume` is distinct from author
`/root/sdk_dependency_probe`. This does not close B01/B02/B03 or any physical
criterion, and does not approve hosted integration without root's checks.

I read all472 lines of the new Rust consumer, the package/lock/toolchain files,
contract, admission, relevant exact upstream implementation, single CI job and
the bounded author claims. All52 author artifact bindings verify. The four
compiled inputs remain byte-identical to first executable freeze
`322d2467b2bcc79064ea8771d2eeb09420913a4d`; main.rs remains SHA256
`cd36d33330990afb17f36564ac262d01936b5e7f00e32d9e42edd37249243b3c`.
No source or expectation was modified for review.

The consumer uses the actual `embedded_io::Read/Write` helpers on a private
wrapper over real blocking UnixStream. The peer uses `std::io` and independently
checks literal `B01PING\n`, then sends literal `B01PONG\n` or the three-byte
prefix. Both configured endpoints must acknowledge readiness before start is
released. The read adapter forwards the OS result and reports completed reads;
nonempty write0 becomes the required WriteZero error. Socket flush is explicitly
not a peer acknowledgement. The fixed stack response is returned only after a
complete, exact match. Failed reads return no response prefix.

Cancellation is caused by `shutdown(Both)` only after the controller observes
three bytes actually read. The peer remains connected in this case. Acceptance
requires a subsequent read0, UnexpectedEof, no read error and the cancel marker;
the fallback timeout cannot pass. The peer-close case separately closes its
write half after the prefix. Timeout requires raw WouldBlock/upstream Other,
zero input and a single read error; the exact upstream std error conversion
does not map WouldBlock to TimedOut. Event ordering permits normal cross-thread
notification interleavings without replacing the actual I/O evidence.

Each operation owns a new pair, its private buffer and both JoinHandles. Actual
shutdown/drop precedes Closed notifications. The controller drops its clones,
performs both joins before inspecting either result, and only then publishes or
prints PASS. Observation failures initiate both shutdowns and still attempt both
joins; a watchdog kill or failed join is never success. There is no retry, replay,
detached-success path, shared connection reuse or exported SDK API. This does not
qualify arbitrary OS/thread failure recovery or hardware cancellation.

## One independent standalone replay

[Preflight](preflight.json) records a fresh Git archive of the exact candidate
package into `/goal/b01-host-stream-consumer-review-runtime/export`. It contains
the four compiled inputs plus README, no Git directory or sibling project.
The new Cargo home received only three registry cache/index files from the
verified author cache: no resolved source tree or compiled artifact was copied.
Cargo unpacked the official crate anew. There was no network acquisition,
installation or global configuration change, and the target directory was new.

[Commands](commands.json) bind one `cargo build --locked --offline --release
--target x86_64-unknown-linux-gnu` and exactly one default runtime invocation under
the admitted30s external watchdog. The build finished before the watchdog began.
Rust1.95.0 identifies compiler59807616e1fa2540724bfbac14d7976d7e4a3860;
Cargo1.95.0 and Linux6.12.101+deb13-amd64 are captured. The actual reviewer ELF is
622384 bytes, SHA256
`1b40f6d44a8363b6e043e7962856f7ae8bf17524c5525b771159becffbaa6dfc`.
It differs from the author ELF; no general reproducibility claim follows.

The [complete original runtime trace](07-smoke.stdout.log) records:

| Case | Independent actual observation |
| --- | --- |
| Response | Ready from both endpoints before I/O; literal request8/response8; exact response published after both joins |
| Timeout | Configured100ms; actual read100591µs; WouldBlock/Other/errno11, no response; peer EOF, close and both joins |
| Cancel | Read3, controller shutdownBoth, next read0; UnexpectedEof, no response; peer EOF, close and both joins |
| Peer EOF | Read3 then read0 after peer write-half close; UnexpectedEof, no response; close and both joins |

The single default invocation exits0, four cases pass, and all eight endpoint
threads join. No additional focused/runtime campaign was run. Author early and
standalone receipts remain separate executions; their passing fmt/Clippy results
are reused by exact source correspondence, not called new reviewer runs. No
review build/runtime/source-check failure occurred. The author's first-build
completion-timestamp clarification remains intact, not relabelled as a start time.

Resolved metadata has exactly the consumer and `embedded-io0.7.1`, with only
`std`/`alloc` enabled and no enabled dependency of embedded-io. The actual crate
archive hashes9eb1aa714776b75c7e67e1da744b81a129b3ff919c8712b5e1b32252c1f07cc7,
and its unpacked lib.rs hashes1077dd3ed8cc4c44d2da1ef5b1e6f4322191b3e25c12407ace75df55b9083963.
[Source checks](source-checks.json) compare actual lib/manifest/full license bytes
to the archive and verify all exported inputs remain unchanged after build/run.
There is no enabled defmt, Nostr, sibling/path dependency or copied upstream code.

## Automatic regression and limits

The actual YAML parses as one PR/main-push Linux job, using the admitted immutable
checkout action and Rust1.95.0. It runs fmt, Clippy with warnings denied, locked
release build, then the binary without arguments under the watchdog. No step
condition or continue-on-error skips the cases. This is paired with source review
of main's fixed four-case loop and the real default replay above, not a text-only
check of PASS labels. The configuration was inspected and structurally parsed;
no hosted job was triggered or observed by the reviewer.

The100ms/1s I/O,3s channel and30s process limits remain experiment inputs. A read
timeout is per I/O call, not a generic total-operation or hard real-time promise.
The watchdog is an experiment boundary and does not prove kernel quiescence in
every failure. This review selects no MCU, SE, electrical interface, SDK driver,
entropy/custody/consent/lifecycle/reset policy, hostile-application isolation,
Board support or physical/release qualification. Root remains responsible for
hosted CI, protected integration and actual-main acceptance.
