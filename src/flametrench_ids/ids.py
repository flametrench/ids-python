# Copyright 2026 NDC Digital, LLC
# SPDX-License-Identifier: Apache-2.0

"""Core identifier encode/decode + generation logic.

Mirrors @flametrench/ids (Node) and flametrench/ids (PHP) exactly. The same
spec fixtures verify all three implementations.
"""

from __future__ import annotations

import re
import sys
import uuid
from dataclasses import dataclass

# UUIDv7 source. Python 3.14 added uuid.uuid7 to the stdlib; older versions
# use the `uuid7` package, which produces an identical RFC 9562 v7 layout.
if sys.version_info >= (3, 14):
    def _uuid7() -> uuid.UUID:
        return uuid.uuid7()
else:
    from uuid7 import uuid7 as _uuid7_str

    def _uuid7() -> uuid.UUID:
        return uuid.UUID(str(_uuid7_str()))


class InvalidIdError(ValueError):
    """Raised when a string is not a syntactically valid wire-format ID."""


class InvalidTypeError(ValueError):
    """Raised when a type prefix is not in the registered set."""


# Registered type prefixes for Flametrench v0.1.
#
# Keep this map synchronized with the Flametrench specification's reserved
# prefix registry at https://github.com/flametrench/spec/blob/main/docs/ids.md.
# Parallel implementations (Node, PHP, Java) use the same prefixes.
TYPES: dict[str, str] = {
    "usr": "user",
    "org": "organization",
    "mem": "membership",
    "inv": "invitation",
    "ses": "session",
    "cred": "credential",
    "tup": "authorization_tuple",
}


@dataclass(frozen=True)
class DecodedId:
    """The shape returned by :func:`decode`.

    ``uuid`` is the canonical 8-4-4-4-12 dashed form (RFC 4122 / 9562).
    """

    type: str
    uuid: str


_HEX_PAYLOAD_LENGTH = 32
_HEX_PATTERN = re.compile(r"^[0-9a-f]{32}$")
_VERSION_NIBBLE_PATTERN = re.compile(r"^[1-8]$")


def _assert_type(type_: str) -> None:
    if type_ not in TYPES:
        registered = ", ".join(TYPES.keys())
        raise InvalidTypeError(
            f"Unregistered type prefix: '{type_}'. Registered prefixes: {registered}.",
        )


def _is_valid_uuid_string(value: str) -> bool:
    """Match the JavaScript ``uuid.validate`` semantics for wire input.

    Accepts canonical 8-4-4-4-12 hex with hyphens, case-insensitive.
    Returns False for anything else (including non-RFC-4122 layouts).
    """
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    # ``uuid.UUID`` accepts URN, braces, and 32-char hex without dashes; we
    # require the canonical dashed form to match the Node/PHP behavior.
    if len(value) != 36:
        return False
    if value[8] != "-" or value[13] != "-" or value[18] != "-" or value[23] != "-":
        return False
    return True


def encode(type_: str, uuid_str: str) -> str:
    """Encode a type and UUID into Flametrench wire format.

    >>> encode("usr", "0190f2a8-1b3c-7abc-8123-456789abcdef")
    'usr_0190f2a81b3c7abc8123456789abcdef'

    :raises InvalidTypeError: If the type prefix is not registered.
    :raises InvalidIdError: If the UUID is not a valid UUID string.
    """
    _assert_type(type_)
    if not _is_valid_uuid_string(uuid_str):
        raise InvalidIdError(f"Value is not a valid UUID: {uuid_str}")
    hex_payload = uuid_str.replace("-", "").lower()
    return f"{type_}_{hex_payload}"


def decode(id_: str) -> DecodedId:
    """Decode a Flametrench wire-format ID into its type and canonical UUID.

    >>> decode("usr_0190f2a81b3c7abc8123456789abcdef")
    DecodedId(type='usr', uuid='0190f2a8-1b3c-7abc-8123-456789abcdef')

    :raises InvalidIdError: If the ID is malformed.
    :raises InvalidTypeError: If the type prefix is not registered.
    """
    if not isinstance(id_, str):
        raise InvalidIdError(f"ID must be a string: {id_!r}")
    separator = id_.find("_")
    if separator == -1:
        raise InvalidIdError(f"ID missing type separator: {id_}")

    type_ = id_[:separator]
    hex_payload = id_[separator + 1 :]

    _assert_type(type_)

    if len(hex_payload) != _HEX_PAYLOAD_LENGTH or not _HEX_PATTERN.match(hex_payload):
        raise InvalidIdError(f"ID payload is not 32 lowercase hex characters: {id_}")

    # Version nibble (13th hex char, 0-indexed position 12) must be 1-8.
    # This rejects the Nil UUID (v0) and Max UUID (v15/f), which are not
    # meaningful identifiers in the Flametrench wire format.
    if not _VERSION_NIBBLE_PATTERN.match(hex_payload[12]):
        raise InvalidIdError(f"ID payload is not a valid UUID: {id_}")

    canonical = "-".join(
        [
            hex_payload[0:8],
            hex_payload[8:12],
            hex_payload[12:16],
            hex_payload[16:20],
            hex_payload[20:32],
        ]
    )
    return DecodedId(type=type_, uuid=canonical)


def is_valid(id_: str, expected_type: str | None = None) -> bool:
    """Check whether a string is a valid Flametrench wire-format ID.

    Optionally asserts the ID is of a specific type.

    >>> is_valid("usr_0190f2a81b3c7abc8123456789abcdef")
    True
    >>> is_valid("usr_0190f2a81b3c7abc8123456789abcdef", "org")
    False
    """
    try:
        decoded = decode(id_)
    except (InvalidIdError, InvalidTypeError):
        return False
    if expected_type is not None and decoded.type != expected_type:
        return False
    return True


def type_of(id_: str) -> str:
    """Extract the type prefix from a wire-format ID.

    :raises InvalidIdError: If the ID is malformed.
    :raises InvalidTypeError: If the type prefix is not registered.
    """
    return decode(id_).type


def generate(type_: str) -> str:
    """Generate a fresh wire-format ID of the given type.

    Uses UUIDv7 so generated IDs are sortable by creation time.

    >>> generate("usr")  # doctest: +SKIP
    'usr_0190f2a81b3c7abc8123456789abcdef'

    :raises InvalidTypeError: If the type prefix is not registered.
    """
    _assert_type(type_)
    return encode(type_, str(_uuid7()))
