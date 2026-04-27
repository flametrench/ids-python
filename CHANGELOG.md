# Changelog

All notable changes to `flametrench-ids` are recorded here.
Spec-level changes live in [`spec/CHANGELOG.md`](https://github.com/flametrench/spec/blob/main/CHANGELOG.md).

## [v0.2.0rc2] — 2026-04-27

### Added
- New `shr` type prefix registered in `TYPES` for the v0.2 share-token primitive ([ADR 0012](https://github.com/flametrench/spec/blob/main/decisions/0012-share-tokens.md)). `encode("shr", uuid)`, `decode("shr_…")`, and `generate("shr")` now work; the share token store in `flametrench-authz` consumes this prefix.

## [v0.2.0rc1] — 2026-04-25

Initial v0.2 release-candidate. Added the `mfa` prefix per ADR 0008.

For pre-rc history, see git tags.
