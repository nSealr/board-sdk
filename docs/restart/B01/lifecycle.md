# Board firmware and owner lifecycle

Documentary candidate, 20 October 2026; no concrete SE/MCU ownership protocol or
reset/update implementation is admitted. Read [api-and-dependencies.md](api-and-dependencies.md)
for services, exact version tuples and source limitations. The
[source register](source-register.json) binds accepted P01/S02 requirements and
the incomplete H01/S04 proposals; it does not adopt those proposals as facts.

## Trust conditions and authority

There is initially **one trusted firmware image**. Library boundaries cannot
isolate hostile applications or protect a key from deliberately malicious code
that the owner is permitted to install. Owner programmability and protection
against unauthorized replacement require an explicit boot/update-root design;
a locked debug port or a `secure` software flag is not that design.

| Condition | Meaning / authority | Must not imply |
| --- | --- | --- |
| Development | Exact known board/build/configuration used with disposable test identities, documented debug/programming access and no production trust claim. | No secret residency, controlled updates or physical attack resistance merely because tests pass. |
| Owner-secured | Exact target and accepted concrete protocol enforce identified owner roots, secret/object access, authorized update/recovery, lock and fault behavior. Local firmware must verify its enforceable preconditions. | No current board satisfies this condition by this document. An owner-secured image is not a hardware wallet or protection from a deliberately authorized hostile image. |
| Product-qualified | External evidence admits a particular product/profile/assembly/image and measured properties through its release gates. | It is not a third hardware lifecycle state, a command, a descriptor bit or permission to bypass local enforcement. Changing an input can invalidate affected qualification. |

These are separate conditions/evidence, not a three-value ladder. Runtime
generation/state may restrict an operation; it cannot promote the product into
qualification. Normal firmware must not contain an "enable production" setting
that bypasses missing physical/security evidence.

Keep three authorities distinct: MCU image/owner roots and irreversible lifecycle
settings; off-device owner signing/recovery credentials; SE vendor/app update,
factory pairing and immutable object roots. Record which party can replace each
root and whether the owner can actually revoke it. A factory/vendor privilege
surviving wipe remains a residual privilege, not a fresh-owner installation.
Lost credentials do not authorize a developer/backdoor key. No fuse, purchase,
manufacturer contact, factory submission or real-secret ceremony is in B01 scope.

## Transition invariants

Before a transition that affects trust/secret state, stop new operations,
invalidate relevant epochs/handles and pending crypto/UI authorization, quiesce
writers, then enter the concrete protocol's recoverable durable sequence. After
reset, create a fresh runtime epoch and reconcile persisted state before serving
requests; never restore an old session/approval merely because a snapshot exists.
Application policy remains separate from generic local input and key services.

Invalidating a host handle is not revocation of a surviving SE authentication
session. Credential update/delete, MCU reset and an unsuccessful/lost command
response must not be assumed to close that session. The concrete backend needs
source-backed termination/reauthentication/reset semantics and fault proof before
any handle or key operation is available again. No serialized handle is restored
as authority after reboot, update, owner change or hardware replacement.

Each protocol must enumerate its actual objects: MCU flash/RAM/retention/cache,
DMA/controller buffers, SE secret slots/counters/PIN/auth sessions/channel state,
wrapping keys/ciphertexts, boot/update roots/rollback floor and recovery records.
For each record creation, rotation, erase, power/reset retention, authority and
finite/irreversible budget. Clearing an MCU record does not erase an SE; AEAD
validity does not prove freshness, durable completion or owner revocation.

No generic atomic MCU+SE update is assumed. Write-ahead intent, quarantine or
readback are permitted design techniques only when exact device semantics prove
them; a journal alone does not solve a power cut between cross-device mutations.
If durable outcome is unknown, remain locked/recovery-only, expose a bounded
public diagnostic and reconcile using an accepted procedure. Do not let a retry
renew a PIN/counter budget, duplicate an operation or reinstall a revoked owner.

## Required transitions and proof obligations

Rows are required behavior for a later selected protocol, not presently callable
SDK operations. Every row needs exact ordering, interruption points and terminal
outcomes before implementation admission. No common reset command is selected.

| Transition / authority | Objects and durable/fault outcome | Residual state, recovery and proof owner |
| --- | --- | --- |
| Manufacture/development / authorized assembler or developer | Record exact assembly, blank/preconfigured objects, debug and vendor/owner roots. Development uses disposable public-test material; do not provision user keys as an initialization side effect. | Factory pairings and irreversible configuration may exist before enrollment. H01/H02S/H04 supply exact state; manufacturing/secret ceremonies require separate authority. |
| First enrollment / intended owner through an accepted local procedure | Verify target identity/configuration, entropy and owner-control preconditions before creating user material. Bind the admitted owner epoch and object policies. Interrupted enrollment must not expose partial keys or grant unrecorded roots. | Repeated/power-cut enrollment must neither bypass attempts nor exhaust hidden irreversible slots. S04 supplies the actual object/owner protocol; B02/B03 prove bounds and recovery on target. |
| Normal lock/unlock / accepted authentication policy and local application authority | Lock invalidates session handles, pending results/gestures and accessible runtime secrets; unlock creates a fresh bounded session only after complete authentication. Persisted attempt state must survive relevant resets. | Authentication failure/health fault/counter exhaustion leaves no crypto output or old authorization. Physical RAM/SE extraction limits and trusted-firmware assumptions stay explicit. S04 plus application policy; B02/B03 physical fault proof. |
| Same-owner firmware update / current authorized update root | Check exact image/target/version and accepted rollback policy before effects; revoke operations, stage/verify/activate through the selected durable mechanism. Re-establish object and provider preconditions on boot. | A valid signer is not proof that the new firmware is harmless: installing a malicious but authorized image is outside one-image isolation. S04/H01 define which secrets may persist or require destructive reprovisioning; boot/update implementation proves it. |
| Owner update-root rotation / current authority under accepted protocol | Bind the intended next root/version and define the precise cutover where old authority is revoked. Power loss at every step must leave a supported authorized root or a documented locked recovery state. | No period of unbounded dual-root acceptance, silent old-root restoration or permanent lockout hidden as success. Off-device credential custody/recovery is a separate owner responsibility. S04/H01 and actual boot mechanism. |
| Interrupted update / boot-time recovery only | Reconcile authenticated image/journal/rollback state, reject partial or mismatched firmware and invalidate all previous session/results. Do not run a partly written image. | Need a proven known-good boot/recovery route or explicit terminal state; no assumed dual-bank/atomic flash behavior. H01 exact MCU/boot design, B02/B03 power-cut tests. |
| Reset, watchdog or power loss / hardware or authorized software | Inventory each reset domain and retention; invalidate runtime generations before accepting new work. Quiesce/reinitialize relevant DMA, bus and auth/channel state. Persistent counters/roots remain at their real durable values. | Power loss is not necessarily SE reset; wake/hibernate may restore privileged sessions. Bounded recovery cannot reuse prior approval or cached entropy. H01 reset domains and S04 exact SE/open-session protocol; B02/B03 traces. |
| Rollback attempt / rejected unless a separately accepted recovery exception applies | Verify actual enforced rollback floor/version binding; reject old images and stale persistent object formats/owner epochs before exposing secrets. | Signed old firmware may still be vulnerable. Normal flash/AEAD cannot establish a monotonic floor; fuse/counter/endurance constraints require actual design and authority. S04/H01 plus boot implementation. |
| Lost owner credentials / defined destructive or off-device recovery authority | No unauthenticated root change or developer override. If the selected target supports only destructive recovery, enumerate exactly what is irrecoverable and what remains. | Owner data loss/terminal exhaustion must be stated before enrollment; a new board plus recovered application identity does not recover the old board's owner rights. S04 protocol; B03 independent user recovery. |
| Destructive reset / accepted physical/authenticated recovery procedure | Revoke runtime handles; destroy/replace every user-access/encryption/auth credential the concrete protocol requires, reconcile partial reset, and verify residual inventory before offering enrollment. | SE vendor roots, pairings, immutable objects, counters and factory configuration may survive. A successful MCU erase or DeleteAll-shaped API is insufficient. If completion cannot be proved, quarantine/unsupported; S04 and actual target fault evidence. |
| New owner / previous-owner revocation plus proven reset preconditions | Admit enrollment only when previous user and owner privileges are actually revoked for the claimed domains. Fresh epoch must not revive old ciphertext, handle, image or transport/auth state. | Irreversible vendor rights/slot budgets must be explicit. If same-chip re-enrollment is unproven or practically exhausts ordinary use, this lifecycle remains unsupported/product-incompatible pending reviewed choice. S04/H02S, B02/B03 independent takeover/reset tests. |
| Hardware replacement / owner plus application recovery protocol | Treat a different board/SE/provider identity as a new target. Re-enroll owner controls and import only intentionally recovered application material through an accepted path. Reject old physical handles/configuration as foreign. | Provider-resident nonexportable keys may be lost; application backups must state exact recovery bytes/derivation. Preserve original scalar representation; equal public keys do not prove equal backup material. S04/K01 and B03 independent recovery. |

## Current unresolved dependencies and compatibility

S04 `e823fec` is an incomplete, unreviewed source checkpoint. TM-HMAC-1 is a
failed reusable-Board proposal; its finite policy budget is not a universal
silicon limit. No successor reset/owner protocol is accepted. Safe7 factory
provisioning is reference behavior, not generic owner transfer proof. Public
NXP middleware alone does not prove exact applet/power-cut/owner-SCP deletion
semantics. A TROPIC advisory's applicability/remedy needs the actual tuple;
dual-SE composition cannot be inferred from two part names. B01 adopts none of
these as an enforceable lifecycle. H01 `40cdb6c` likewise supplies incomplete
host/panel/reset proposals, not an admitted device configuration.

Before a lifecycle driver addendum, S04/H01/H02S/H04 must supply the actual
object/authority/reset/boot/entropy/electrical contract with referenced exact
part/configuration and unresolved failures. B02 then specifies executable scope,
images, finite bounds, models where useful and physical negative/power-cut tests.
Models are checked against sourced assumptions; they do not prove unmeasured SE
atomicity. B03 binds release evidence to actual independent consumer/recovery
behavior. The literal B01 hardware-pinning criterion remains pending H04.

No code, fake success stub, enclave/multi-app isolation, production qualification
or tested lifecycle follows from this document. A final distinct substantive
review must check this exact candidate before accepting even its bounded
documentary result. Actual A02 layout/current H01/S04 source reconciliation and
normal protected integration remain separate steps.
