# flametrench-ids

Python SDK for the [Flametrench v0.1](https://github.com/flametrench/spec) wire-format identifier specification.

Flametrench identifiers are stable, opaque strings of the form `{type}_{32-hex}`, where the hex payload is a UUIDv7 (so generated IDs sort by creation time). The same identifiers travel unchanged across Node, PHP, Python, and Java SDKs.

```python
from flametrench_ids import generate, decode, is_valid, type_of

generate("usr")
# → 'usr_0190f2a81b3c7abc8123456789abcdef'

decode("usr_0190f2a81b3c7abc8123456789abcdef")
# → DecodedId(type='usr', uuid='0190f2a8-1b3c-7abc-8123-456789abcdef')

is_valid("usr_0190f2a81b3c7abc8123456789abcdef", "usr")  # → True
is_valid("usr_0190f2a81b3c7abc8123456789abcdef", "org")  # → False

type_of("usr_0190f2a81b3c7abc8123456789abcdef")  # → 'usr'
```

## Installation

```bash
pip install flametrench-ids
```

Requires Python 3.11+. UUIDv7 generation uses `uuid.uuid7()` from the stdlib on Python 3.14+, falling back to the [`uuid7`](https://pypi.org/project/uuid7/) package on 3.11–3.13. Both produce identical RFC 9562 v7 layouts; the conformance suite verifies this.

## Registered type prefixes

| Prefix  | Meaning                |
| ------- | ---------------------- |
| `usr`   | user                   |
| `org`   | organization           |
| `mem`   | membership             |
| `inv`   | invitation             |
| `ses`   | session                |
| `cred`  | credential             |
| `tup`   | authorization tuple    |

The registry is normative; see [docs/ids.md](https://github.com/flametrench/spec/blob/main/docs/ids.md) for the full rules.

## Conformance

`flametrench-ids` runs the same fixture corpus that gates `@flametrench/ids` (Node) and `flametrench/ids` (PHP). All 48 MUST-level fixtures from `spec/conformance/fixtures/ids/` pass on every release; the test suite vendors the fixtures and compares them to the upstream spec repo via CI.

```bash
# In a checked-out copy:
pytest
```

## License

Apache-2.0. See [LICENSE](./LICENSE) and [NOTICE](./NOTICE).

Copyright 2026 NDC Digital, LLC.
