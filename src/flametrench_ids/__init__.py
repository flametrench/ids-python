# Copyright 2026 NDC Digital, LLC
# SPDX-License-Identifier: Apache-2.0

"""flametrench-ids — wire-format identifiers for Python.

The spec-normative identifier layer for Flametrench v0.1. See the upstream
specification at https://github.com/flametrench/spec/blob/main/docs/ids.md.

The wire format is ``{type}_{32-hex}``. Generated IDs use UUIDv7 so they
sort by creation time. The same fixtures that exercise the Node and PHP
SDKs run against this package; cross-language interop is enforced by the
test suite, not aspiration.
"""

from .ids import (
    TYPES,
    DecodedId,
    InvalidIdError,
    InvalidTypeError,
    decode,
    decode_any,
    encode,
    generate,
    is_valid,
    is_valid_shape,
    type_of,
)

__all__ = [
    "TYPES",
    "DecodedId",
    "InvalidIdError",
    "InvalidTypeError",
    "decode",
    "decode_any",
    "encode",
    "generate",
    "is_valid",
    "is_valid_shape",
    "type_of",
]

__version__ = "0.1.0"
