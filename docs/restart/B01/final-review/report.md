# B01 distinct final documentary review

**Verdict: PASS_bounded_documentary_only.** No blocking defect was found in
`nSealr/board-sdk@27308eb7eb80bce22f411f9d40da159d901b7087`. This accepts the
four documentary decisions within the previously admitted scope. It does not
complete B01, select a dependency/part/protocol, admit an executable API, or
qualify a physical or cryptographic boundary. Literal parent criterion 2 remains
pending the actual H04 electrical artifact. Ordinary integration stays held for
actual A02 paths and current H01/S04 reconciliation.

Reviewer: `/root/b01_final_review`, distinct from candidate author `/root`.
Review date: 2026-10-20. Owned branch: `review/b01-final`. Only this
`final-review/` directory was written. No authored output, source main, task
graph, other worktree, or hardware was changed. The 2026-10-20 resumption and
latest Sol default policy supersede the historical pause/model instructions;
no additional agents or model escalation were used for this review.

## Exact scope and requirements

The candidate's sole parent is preparation acceptance
`8377f9264ca0c426dad0d79578c01be2e1d32509`. Its entire delta consists of four
added files: `api-and-dependencies.md`, `lifecycle.md`, `source-register.json`
and `result.json`. The accepted brief, acceptance plan, source audit and
preparation acceptance were read before the outputs. Preparation-review hashes
were checked against distinct review
`09bd394a6fc1502f192ee84cd99ad6ceb5e40f07`.

All four parent acceptance strings in the audit, plan and result equal the
actual B01 record in `nSealr/nsealr@f2ef70f522af4977e15f81554a8c6eadcdbe8097`.
The unchanged parent criteria, rather than the candidate's statements about
itself, determine the dispositions below. The enclosing candidate commit binds
`result.json`; its other three artifact hashes match actual committed bytes.
It claims neither a self-hash nor an already completed final review.

| Parent index | Documentary assessment | Parent criterion disposition |
| --- | --- | --- |
| 0 — generic services without Nostr policy | PASS documentary only: eight service rows plus shared operation rules define callers, owners, buffers, completion, bounds, errors, cancellation, retained state and proof owners. | Pending actual supported service implementation and its evidence. No executable exposure is claimed. |
| 1 — one trusted firmware image | PASS documentary only: the initial model and absence of hostile-application isolation are explicit; source extraction is deliberately deferred without a real consumer. | Pending the useful independent consumer/implementation evidence. No empty crate or success stub was introduced. |
| 2 — actual electrical pinning and compatibility | PASS for the specified format, rejection rules and acyclic dependency decision. | **Pending H04 actual electrical pinning.** A tuple format does not satisfy the literal requirement. |
| 3 — development/owner/product conditions and reset | PASS documentary only: authority, residual privileges, transitions and failure/recovery obligations are explicit. | Pending accepted concrete S04/H01/H02S/H04 protocols and implementation/physical proof. |

## Source and semantic assessment

This was a source review, not a headings/presence test. The independent
`verify.py` probe checked Git objects and parsed the actual published archives;
manual review read the corresponding interface bodies and pinned project
source. Existing extracted files used for reading were compared to archive
members. The probe was authored in this review directory and did not execute
the author's register builder or install/compile a dependency.

**Dependency and extraction decisions.** The core `nip19.rs` implementation
stores a 32-byte software scalar, validates it in `take_from`, wipes the input,
has explicit secret encoding paths and wipes its current array on drop. It
cannot become an SE handle through a type alias. `session/keyring.rs` retains
Nostr/raw-key/BIP39 sources and labels; `review/buttons.rs` returns application
`ReviewButton` values, and `review/display.rs` renders review actions/pages.
The candidate correctly retains these modules in the engine. Their core
manifest declares MIT; ownership/source remains nSealr, and no code is copied.
There is no selected generic consumer to justify extraction, reverse Nostr
dependency or a utility crate. Prospective diagnostic/key consumers are clearly
future consumers, not existing proof. Static capability, local state and external
release admission remain separate; neither diagrams nor a global boolean grant
trust.

**Bus, power and timing.** The actual `embedded-hal 1.0.0`
`src/spi.rs:134-160,347-363,438-481` allows bus completion before idle and makes
device transaction locking implementation-defined; error CS deassertion is an
attempt. `src/i2c.rs:41-48` requires idle completion. `src/delay.rs:9-44` gives
minimum delays. The async SPI body supplies no universal cancellation guarantee.
The candidate correctly requires target-specific lock, poll, transfer, cleanup
and terminal recovery bounds. It does not promise an executor timeout will stop
a blocking poll. Bus ownership distinguishes private SE/review access from
expansion. Power transitions inventory real reset domains, external power and
retained state rather than treating rail-off as erase. No pins, voltages,
drivers, numerical deadlines or board defaults were guessed.

**Streams, cancellation and entropy.** The actual async stream helper loops
advance their slice after each completed suboperation
(`embedded-io-async 0.7.0 src/lib.rs:49-78,119-148`); primitive cancellation
safety is encouraged, not required. Blocking stream helpers also permit partial
progress and blocking waits. The candidate forbids replaying side effects from
a cancelled compound helper and requires correlation/reconciliation above the
stream. `rand_core 0.10.1 src/lib.rs:189-200,225-249` carries fallible errors but
requires no destination wiping; `src/unwrap_err.rs:31-53` converts errors into
panic. The candidate therefore preserves S02's stronger all-or-error boundary:
every **returned** error wipes the whole caller destination, produces no crypto
output, and retains no previous bytes for reuse. Quiescing DMA/writers precedes
wiping and returning/reusing memory. Unproved cleanup leads to poisoned service
and supported terminal recovery, not an error return while hardware still owns
the buffer. Provider selection, health, actual invocation and bounded faults
remain future target proof. No weak or panic fallback is admitted.

**Keys, storage, display and input.** Key references bind provider/board/object,
exact algorithm/parameters/purpose and owner/session/lifetime; foreign, stale,
revoked and wrong-purpose references reject. Raw scalars, native BIP340,
nonexportability and human consent are not inferred from a handle. Recovery
preserves original representation and belongs to the application/protocol.
Storage distinguishes committed/not committed/unknown durable outcome and
requires reconciliation before another mutation; AEAD/integrity does not become
antirollback. The actual graphics trait accepts arbitrary iterators and can use
`Infallible` for RAM drawing (`embedded-graphics-core 0.4.0
src/draw_target/mod.rs:281-304,388-424`). Even its fill helper can return success
for a short color iterator. The candidate adds a bounded adapter requirement and
separates RAM drawing, transport, controller and visible refresh; it claims none
of those properties from a successful drawing call. Input event ownership,
boot-held controls, safe release/rearm, time/queue limits and presentation/session
epochs prevent generic events from minting application authority. Actual
electrical attribution, physical input and visible presentation still need
their named proof owners.

**Lifecycle and current context.** The transition table covers manufacture,
enrollment, lock/unlock, same-owner update, root rotation, interrupted update,
reset/power loss, rollback, lost credentials, destructive reset, new owner and
hardware replacement. Shared rules require quiescence, generation invalidation,
durable reconciliation and no stale results. Root rotation requires an explicit
cutover and bounded residual authority. MCU owner roots, off-device credentials,
SE platform/pairing/vendor privileges and immutable objects are separate.
Unknown cross-device outcomes remain locked/recovery-only; neither a journal nor
a DeleteAll-shaped call proves atomic erasure or old-owner revocation. Finite
attempt/use/pairing budgets and practically disposable lifecycle proposals remain
product incompatibilities requiring review. Signed old firmware and valid AEAD
records are not treated as a monotonic rollback floor.

The pinned S04 `e823fec` source says TM-HMAC-1 fails reusable-Board acceptance;
its 2048 combined-use policy is not an inherent silicon limit. Its original
scalar and factory/root/reset limits support the candidate's cautions. The
H01 `40cdb6c` checkpoint likewise admits no host configuration. New H01
`e35ee73b53813b2892267edf9a07088b4a7c0036` cache/GPIO/watchdog notes and S04
`f7af3616c5310686f2cbbc37dbfdf247b0d10cc0` session notes are treated as
**unreviewed requirements context**. Host epoch invalidation is expressly
distinguished from surviving backend authentication sessions, including lost
responses and credential deletion/update. Historical SE050 behavior is not
promoted to exact SE051C2 admission. This review did not independently admit those
hardware/protocol proposals or certify their original manuals.

## Verification and remaining gates

`python3 docs/restart/B01/final-review/verify.py --refresh-upstream --receipt
docs/restart/B01/final-review/verification.json` exited 0. Its receipt records:

- All 36 unique project Git file bindings matched mode, blob, path, bytes and
  SHA256; all 25 preparation-audit rows were also verified.
- All six official crate archives matched the stored exact-version registry
  checksums, byte lengths and declared archive member hashes. Parsed manifests
  matched declared features, dependencies, license, repository, Rust version
  and VCS information. All six remain surveyed only.
- Eighteen fresh official responses matched byte-for-byte in memory: six
  archives, ten immutable upstream source bodies and two graphics root licenses.
- The graphics 0.4.0 archive has no license-body members. Its MIT/Apache license
  declaration and separately sourced exact upstream root blobs are correctly
  distinguished. The rand_core stale crate-level origin and two historical 404
  records are preserved; the exact version manifest/metadata points to
  `rust-random/rand_core` and its source bodies match the archive.
- Candidate diff scope and whitespace checks passed. SDK/core/hardware main
  references remained `043e64c` / `f2ef70f` / `340697d` during review.

An initial read-only inspection used the unavailable `python` command; rerunning
with `python3` succeeded. No product failure or unverified result was inferred
from that tooling alias. No product suite, prose-presence test, SDK compilation,
installation, hardware operation, fuse/key ceremony or physical measurement was
appropriate to this documentary-only delta. The source probe's success proves
identity/correspondence; the semantic conclusions above are the distinct review.

Blocking review findings: **none**. Remaining requirements are recorded without
weakening them: actual H04 electrical artifact; concrete accepted lifecycle and
target configuration; real B02/B03 consumer/service/provider/recovery evidence;
and actual A02/current H01/S04 reconciliation before ordinary integration.
Changing an authored output invalidates this exact-candidate review.
