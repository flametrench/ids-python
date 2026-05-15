# Changelog

All notable changes to `flametrench-ids` are recorded here.
Spec-level changes live in [`spec/CHANGELOG.md`](https://github.com/flametrench/spec/blob/main/CHANGELOG.md).

## [v0.3.0] — 2026-05-15 (tagged; PyPI publish pending org approval)

### Added
- New `pat` type prefix registered in `TYPES` for the v0.3 personal-access-token primitive ([ADR 0016](https://github.com/flametrench/spec/blob/main/decisions/0016-personal-access-tokens.md)). `encode("pat", uuid)`, `decode("pat_…")`, and `generate("pat")` now work; the PAT store in `flametrench-identity` consumes this prefix.

### Release status
- Tagged in lockstep with the Node and PHP v0.3.0 cuts; PyPI publication remains externally blocked (the `flametrench` org approval that has held since v0.2.0). Wheels build locally; `pip install -e ../ids-python` from a sibling checkout works for downstream consumers.

## [v0.2.0rc3] — 2026-04-27

### Fixed
- UUIDv7 fallback import on Python 3.11–3.13. The PyPI distribution `uuid7` exposes its module as `uuid_extensions` (the dist name and module name don't match), so the fallback `from uuid7 import uuid7` raised `ModuleNotFoundError` on every Python below 3.14. Local development happens on Python 3.14 (which uses the stdlib `uuid.uuid7()` fast path), so the broken fallback never surfaced until CI exercised it. Now imports `from uuid_extensions import uuid7` correctly.

## [v0.2.0rc2] — 2026-04-27

### Added
- New `shr` type prefix registered in `TYPES` for the v0.2 share-token primitive ([ADR 0012](https://github.com/flametrench/spec/blob/main/decisions/0012-share-tokens.md)). `encode("shr", uuid)`, `decode("shr_…")`, and `generate("shr")` now work; the share token store in `flametrench-authz` consumes this prefix.

## [v0.2.0rc1] — 2026-04-25

Initial v0.2 release-candidate. Added the `mfa` prefix per ADR 0008.

For pre-rc history, see git tags.
