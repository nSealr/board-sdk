# nSealr Board SDK

Generic platform software for nSealr Board, independent of Nostr.

**Status: development foundation. No implemented or qualified board support is claimed yet.** Component selection and physical lifecycle experiments precede driver commitments.

This repository will own board support, peripheral/secure-element drivers, boot/update/recovery integration, owner-controlled provisioning and standalone examples. The [Nostr Signer](https://github.com/nSealr/nsealr) owns Nostr semantics; the [hardware repository](https://github.com/nSealr/hardware) owns electrical and mechanical design.

## First acceptance target

An independent developer can build, flash, run, update, reset and recover one standalone non-Nostr example on an identified board revision using documented interfaces. The record must include toolchain, source/binary hashes, lifecycle state, physical results and limitations.

One trusted firmware image is the first execution model. Linked SDK libraries do not provide isolation between mutually hostile applications. Authentication, SSH and wallet firmware are possible downstream projects, each requiring its own protocol, algorithm and security qualification.

## Scope and organization

Create `crates/`, `examples/` and `tools/` as real implementations land; no empty driver hierarchy is required now. Keep one clear support manifest for exact board/silicon/SE revisions, active interfaces and update/recovery behavior. Pin dependencies and prefer upstream drivers where their behavior has been verified.

The initial task ownership is B01–B03 in the [project task graph](https://github.com/nSealr/nsealr/blob/main/plan/work-items.json). Hardware freeze is a separate gate; this SDK does not silently choose an MCU or two secure elements.

## Reviewed design inputs

B01 documentary work describes proposed [service and dependency boundaries](docs/restart/B01/api-and-dependencies.md) and [owner lifecycle requirements](docs/restart/B01/lifecycle.md). Electrical pinning, service implementation and physical qualification remain open; these documents do not claim supported hardware or an implemented SDK.

## Security boundaries

- No Nostr-specific account/event/policy semantics in the platform.
- No private SE bus or trusted review path exposed as unrestricted expansion GPIO.
- Firmware replacement/reset must account for persistent MCU and SE objects, not only erase application flash.
- Development and qualified-product lifecycles declare their trust roots and irreversible settings explicitly.
- Physical acceptance, recovery and advisory handling are required before support is advertised.

## License

MIT; see [LICENSE](LICENSE). Third-party implementations keep their original notices and licensing.
