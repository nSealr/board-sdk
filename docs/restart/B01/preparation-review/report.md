# B01 distinct preparation review

**PASS for documentary preparation only.** The exact candidate is
`c82b065f30309c5a8f3db3e81f8addfce7b8ad30`. This accepts the proposed bounded work
in the three preparation files. It does not complete B01, select dependencies,
authorize executable SDK source, admit hardware or approve lifecycle operations.

Reviewer: `/root/h01_author`, Astra xhigh, distinct from author `/root`,
2026-10-18. Review branch `review/b01-spec`, separate owned checkout. Only
`docs/restart/B01/preparation-review/` was written. The author checkout,
canonical graph, source mains and H01 author worktree were left unchanged.

## Exact source and scope checks

The [read-only probe](probes/check_bindings.py) and its
[result](logs/bindings.json) verify all25 source-audit rows against actual Git
objects: repository/commit/path, mode, blob, byte length and SHA256. All four
parent criteria match the graph at
`nsealr@f2ef70f522af4977e15f81554a8c6eadcdbe8097` verbatim in both preparation
JSON files. The SDK base `043e64c` has exactly the four stated foundation files;
the candidate adds only the three preparation files. The exact candidate passes
`git diff --check`. File hashes are also bound in [review.json](review.json).

These checks establish provenance and scope. The substantive assessment below
comes from reading the complete preparation, actual canonical architecture,
repository decisions, S02 entropy contract, P01 generic threat model and
requirements, A01 disposition, and the relevant current source bodies. No
source-count or prose-existence test is used as API or hardware acceptance.

## Four unchanged criteria

| Parent criterion | Preparation assessment | Acceptance still required |
| --- | --- | --- |
|0: generic buses/power/entropy/key handles/algorithms/storage/display/input/lifecycle without Nostr schemas or policy | **PASS.** SDK-01/02 enumerate all services and require callers, owners, error/cancellation/reset semantics, retained state and finite resource policy. The acyclic direction is explicit. Key custody, algorithm support, consent and release admission are separated. | Actual API/dependency decision with reviewed primary interfaces and concrete future consumers. No SDK service is implemented by this preparation. |
|1: libraries in one trusted image; no inter-application isolation | **PASS.** The brief and README explicitly reject hostile-application isolation from linkage/types and forbid an unused plugin/universal-HAL scaffold. SDK-05 requires an accepted addendum before any real crate/example. | Maintain this boundary in the actual decision; a future standalone non-Nostr build/run belongs to its implemented consumer and B02/B03. |
|2: exact electrical contracts and version compatibility without circular/sibling dependencies | **PASS for planning, actual pinning pending.** SDK-03 names board/artifact/MCU/package/revision/SE configuration/pin/rail/driver/root compatibility. Unknown tuples reject. It explicitly preserves the literal parent criterion as pending until H04 supplies a reviewed actual contract. | Do not declare B01 complete on a schema, proposed tuple or inherited BOM. Reconcile A02 paths and exact H01/H04 inputs before integration. This is a real dependency, not an implicit waiver. |
|3: developer/owner-secured/product-qualified transitions and secret-reset limits | **PASS.** SDK-04 distinguishes owner MCU roots, off-device credentials and vendor SE authority. It covers enrollment, lock/unlock, authenticated update/root rotation, interruption, rollback, credential loss, reset, new owner and replacement, with surviving objects, failure ordering and physical proof owners. Product qualification is external evidence, not a firmware flag. | Produce the actual transition/residual-state decision against S04/H01 and exact chip behavior. Re-enrollment, counter exhaustion, irreversible limits and lost-authority outcomes cannot become an optimistic universal reset API. |

There are no blocking preparation findings. These four preparation verdicts are
not four completed B01 acceptance results. In particular, criterion2 cannot be
satisfied by this candidate and is explicitly retained as a future prerequisite.

## Source and boundary substance

The observed extraction claims are supported by actual source. At the pinned
core revision, `nip19.rs` defines an owned32-byte scalar, validates input range,
clears the input and wipes the current backing array on drop. It is not an SE
object or proof that all physical copies disappear. `session/keyring.rs` owns
NIP-19/BIP-39 session material. `review/buttons.rs` directly imports
`ReviewButton`; `review/display.rs` consumes review actions and constructs
approval hints. Those whole modules cannot become a Nostr-independent platform
merely by moving them. A smaller utility might later be reusable, but the brief
correctly requires a named generic consumer and a retain/extract/leave decision
first. It does not claim that no generic utility can ever exist.

The accepted A01 disposition retains the MIT SDK foundation and requires used
generic APIs/examples. It also keeps review semantics in the product core and
requires provenance on actual imports. The brief's refusal to fabricate an
extraction or an empty crate is consistent with that decision and the B01
required evidence, which asks for a standalone scaffold only when used.

S02's actual entropy contract has no production provider and requires fallible
all-or-error output, whole-destination cleanup on failure, bounded retry and
actual linked/runtime provenance. SDK-02 preserves those obligations without
importing Nostr-specific scalar/purpose semantics. It also handles the concrete
driver hazard that an outer cooperative timeout cannot interrupt an inner
blocking poll. The later API decision must allocate responsibility for cleanup
and cancellation rather than assuming any upstream trait enforces it.

The preparation correctly treats H01 `e39015a` and its distinct `9d5ed3b`
review as incomplete context. I checked the actual result's open acceptance and
remaining gates and the review's limited verdict/next-signoff requirements.
Neither admits a host, panel, pin mapping or complete lifecycle. Subsequent H01
research is not silently adopted here; the brief requires reconciliation before
implementation/integration. Hardware main's older navigation is not the current
Board contract.

Owner-programmable general-purpose use is preserved. MCU firmware replacement
must account for privileged SE state, immutable vendor roots, update authority,
terminal budgets and surviving counters. Unsupported transitions must fail
explicitly and be assessed for product viability. This avoids promising either
universal erasure or unlimited re-enrollment. It also avoids forcing a Signer,
FIDO, SSH or wallet protocol into the generic service boundary.

Primary upstream interface/manual research is a required output of the approved
next documentary phase, not evidence already supplied by the25 Git bindings.
No specific HAL, display, storage, entropy trait or crypto dependency is selected
by this review. Before any implementation, the named consumer, exact source and
features, licensing, hidden blocking/cancellation behavior and affected negative
proof must be concrete. The existing brief requires that work; an additional
empty code scaffold is neither necessary nor authorized now.

## Reading and verification limits

Fresh reading includes all three preparation files and SDK foundation
instructions/README; canonical restart README, architecture and repositories;
B01/B02/B03/S04/H04 graph entries; P01 PROD-02/11/12 and hardware/qualification
context, complete threat-model text; A01 disposition/result; S02 entropy
contract; core Cargo/lib; `nip19.rs`1–175, `keyring.rs`1–145, and selected
button/display types and actual rendering/event functions. A first broad source
excerpt exceeded the output limit; it was not treated as full reading. The
relevant scalar/keyring and generic-threat-model bodies were then read directly.
The25 binding checks cover complete bytes even where semantic reading is
selected. This is not a new comprehensive audit of the core or H01 manuals.

The binding probe passed once, with no source-binding failures. No product test
suite was rerun because this is documentary preparation with no executable
product changes. No external participant was contacted, dependencies installed,
hardware operated, secrets used, source extracted or production flags changed.
The parent must still arrange a distinct exact final review of B01's actual
documentary result; changed preparation invalidates affected portions of this
verdict.
