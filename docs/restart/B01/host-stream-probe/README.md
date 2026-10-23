# B01 real host stream consumer evidence

Author `/root/sdk_dependency_probe`, 23 October 2026. This records an actual
non-Nostr Linux consumer of the selected `embedded-io 0.7.1` interface. It is a
bounded B01 integration experiment; all B01/B02/B03 acceptance criteria remain
open. The frozen [contract](../host-stream-probe-contract.md) at
`7498600d280b11f3d28777ef653037b7fd8328eb` received distinct root scope review and
[admission](../host-stream-probe-acceptance.json) in
`e3cdc8238a1012dca5ae4f5d80f70e35e56998a2` before executable source was written.
Final implementation review and hosted integration are still pending.

The actual [consumer and commands](../../../../examples/host-stream-diagnostic/README.md)
use real Unix sockets and an independent literal-byte peer over `std::io`.
`embedded_io::Read/Write` and their actual `read_exact/write_all` helpers carry
the request and response. The private socket wrapper preserves I/O errors,
observes completed reads and prevents nonempty `write` from returning zero.
Only the complete expected frame can be returned from the consumer; the
controller publishes it after collecting both threads. A partial/error outcome
returns no response buffer and never reuses a connection.

## Source freeze and early smoke

The first implementation was committed as
`322d2467b2bcc79064ea8771d2eeb09420913a4d` before any consumer build/runtime.
[Input freeze](early-smoke/inputs.json) binds its four source inputs, toolchain,
kernel and fixed oracle. `src/main.rs` SHA256 is
`cd36d33330990afb17f36564ac262d01936b5e7f00e32d9e42edd37249243b3c`.
No implementation source changed after this smoke; later changes package
documentation, regression configuration and evidence only.

The [first locked release build](early-smoke/01-build.json) passed. Its actual
622,320-byte ELF SHA256 is
`8051e97d5af7182ef41aaa40eac301e91f8e20aa7b88eabcc838598576cea005`.
The [first runtime](early-smoke/02-run.json), started only after the build under
the external 30 s watchdog, passed all four cases in about 0.106 s.
[Raw output](early-smoke/02-run.stdout.log) preserves the entire phase trace:

| Frozen case | Actual observation |
| --- | --- |
| Start / request / response | Both endpoints ready before request I/O; peer received `42303150494e470a`; complete response `423031504f4e470a` published after joins. |
| Silent timeout | Configured 100 ms blocking read failed after 101,985 microseconds with raw `WouldBlock`, upstream `Other`, errno 11; no response. |
| Local cancellation | Read consumed three bytes after peer sent `423031`; controller shutdown followed; next read returned zero, consumer returned `UnexpectedEof`, no response. |
| Partial peer close | Peer sent `423031`, shut down its write half; consumer read zero after the prefix and returned `UnexpectedEof`, no response. |

Every case observed peer EOF, endpoint shutdown and both actual joins. A fallback
timeout cannot pass the cancellation/EOF match. Format and Clippy with
`-D warnings` also passed; [author receipts](author-checks/) retain exact argv and
stdout/stderr. There was no build/runtime/lint RED. Failed protocol operations
above are required negative cases, not successful response operations.

## Clean standalone proof and dependency closure

[Standalone export](standalone/export.json) records an archive of the exact first
implementation commit, extracted into a new directory containing only the four
package inputs. All four matched the authored source byte-for-byte. It had no
Git checkout, Signer, hardware checkout or sibling package; a new Cargo home and
target directory ensured the second build did not borrow compiled artifacts.

The [standalone commands](standalone/commands.json) record Rust/Cargo 1.95.0,
`x86_64-unknown-linux-gnu`, Linux `6.12.101+deb13-amd64`, fresh locked metadata,
resolved features, fmt, Clippy, release build and the same 30 s runtime watchdog.
Every command passed. [Standalone raw output](standalone/11-run.stdout.log)
again passed the four unchanged cases; the timeout read measured 102,055
microseconds. [Binary identity](standalone/binary.json) binds the actual second
ELF. Build-path differences are not a reproducibility claim.

[Dependency verification](dependency-resolution.json) checks the actual
downloaded 16,035-byte archive against the frozen checksum
`9eb1aa714776b75c7e67e1da744b81a129b3ff919c8712b5e1b32252c1f07cc7` and compares
the resolved source/manifest/license members with archive bytes. Locked metadata
contains exactly this consumer plus `embedded-io`; actual dependency features
are `std` and `alloc`, with no enabled `defmt`, Nostr or path dependency. Both
full third-party license bodies are in the original package. No implementation
or manual body is redistributed here.

## Regression, limits and remaining review

The single [PR/main job](../../../../.github/workflows/host-stream-diagnostic.yml)
pins the already-reviewed checkout action and Rust 1.95.0, then checks fmt,
Clippy, locked release build and all four default runtime cases. Compilation
precedes the runtime watchdog. It has no schedule. Its configuration is part of
the candidate; no hosted CI, PR or integration has been started by this author.

The 100 ms / 1 s / 3 s / 30 s settings are experiment inputs. A socket `flush`
does not establish peer/device completion; kernel buffering, scheduler timing,
general total-operation deadlines, hardware cancellation and failed kernel
quiescence are not qualified. An uncollected worker remains an uncertain,
unavailable outcome, never permission to return/reuse its buffer or connection.

This result selects no MCU, SE, electrical tuple or hardware driver; proves no
entropy, custody, physical consent, lifecycle reset/recovery, hostile-application
isolation, Board support or release guarantee. Distinct final source/behavior
review and root-owned hosted CI/integration remain required. No task/release
graph is changed and no parent criterion is closed.
