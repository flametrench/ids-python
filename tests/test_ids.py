# Copyright 2026 NDC Digital, LLC
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for the Python ids API.

Mirrors the Node + PHP unit tests so behavior is consistent across SDKs.
"""

from __future__ import annotations

import re

import pytest

from flametrench_ids import (
    InvalidIdError,
    InvalidTypeError,
    TYPES,
    decode,
    decode_any,
    encode,
    generate,
    is_valid,
    is_valid_shape,
    type_of,
)

SAMPLE_HEX = "0190f2a81b3c7abc8123456789abcdef"


class TestEncode:
    def test_encodes_a_canonical_uuid(self) -> None:
        result = encode("usr", "0190f2a8-1b3c-7abc-8123-456789abcdef")
        assert result == "usr_0190f2a81b3c7abc8123456789abcdef"

    def test_uppercase_uuid_input_is_lowercased(self) -> None:
        result = encode("org", "0190F2A8-1B3C-7ABC-8123-456789ABCDEF")
        assert result == "org_0190f2a81b3c7abc8123456789abcdef"

    def test_unknown_type_prefix_raises(self) -> None:
        with pytest.raises(InvalidTypeError):
            encode("foo", "0190f2a8-1b3c-7abc-8123-456789abcdef")

    def test_malformed_uuid_raises(self) -> None:
        with pytest.raises(InvalidIdError):
            encode("usr", "not-a-uuid")


class TestDecode:
    def test_round_trip(self) -> None:
        original = "0190f2a8-1b3c-7abc-8123-456789abcdef"
        encoded = encode("usr", original)
        decoded = decode(encoded)
        assert decoded.type == "usr"
        assert decoded.uuid == original

    def test_rejects_missing_separator(self) -> None:
        with pytest.raises(InvalidIdError):
            decode("usr0190f2a81b3c7abc8123456789abcdef")

    def test_rejects_uppercase_hex(self) -> None:
        with pytest.raises(InvalidIdError):
            decode("usr_0190F2A81B3C7ABC8123456789ABCDEF")

    def test_rejects_unregistered_prefix(self) -> None:
        with pytest.raises(InvalidTypeError):
            decode("foo_0190f2a81b3c7abc8123456789abcdef")

    def test_rejects_nil_uuid(self) -> None:
        # All-zeros: version nibble is 0
        with pytest.raises(InvalidIdError):
            decode("usr_00000000000000000000000000000000")

    def test_rejects_max_uuid(self) -> None:
        # All f's: version nibble is f (15)
        with pytest.raises(InvalidIdError):
            decode("usr_ffffffffffffffffffffffffffffffff")


class TestIsValid:
    def test_returns_true_for_valid_id(self) -> None:
        assert is_valid("usr_0190f2a81b3c7abc8123456789abcdef")

    def test_returns_false_for_unregistered_prefix(self) -> None:
        assert not is_valid("foo_0190f2a81b3c7abc8123456789abcdef")

    def test_type_check_returns_true_when_matches(self) -> None:
        assert is_valid("usr_0190f2a81b3c7abc8123456789abcdef", "usr")

    def test_type_check_returns_false_when_mismatched(self) -> None:
        assert not is_valid("usr_0190f2a81b3c7abc8123456789abcdef", "org")


class TestTypeOf:
    def test_returns_the_type_prefix(self) -> None:
        assert type_of("usr_0190f2a81b3c7abc8123456789abcdef") == "usr"

    def test_raises_for_malformed(self) -> None:
        with pytest.raises(InvalidIdError):
            type_of("not an id")


class TestGenerate:
    def test_produces_a_well_formed_id_for_each_registered_type(self) -> None:
        pattern = re.compile(r"^[a-z]+_[0-9a-f]{32}$")
        for type_ in TYPES:
            id_ = generate(type_)
            assert pattern.match(id_)
            assert is_valid(id_, type_)

    def test_unregistered_type_raises(self) -> None:
        with pytest.raises(InvalidTypeError):
            generate("foo")

    def test_generated_ids_are_unique(self) -> None:
        ids = {generate("usr") for _ in range(50)}
        assert len(ids) == 50

    def test_generated_ids_round_trip(self) -> None:
        id_ = generate("org")
        decoded = decode(id_)
        assert decoded.type == "org"
        # Re-encode and compare back to the wire form.
        assert encode("org", decoded.uuid) == id_


class TestDecodeAny:
    """Adapter helper for application-defined object types."""

    def test_decodes_a_registered_prefix_the_same_as_decode(self) -> None:
        result = decode_any(f"usr_{SAMPLE_HEX}")
        assert result.type == "usr"
        assert result.uuid == "0190f2a8-1b3c-7abc-8123-456789abcdef"

    def test_decodes_an_application_defined_prefix_that_decode_rejects(
        self,
    ) -> None:
        # 'proj' is not in TYPES — strict decode raises InvalidTypeError;
        # decode_any accepts it.
        result = decode_any(f"proj_{SAMPLE_HEX}")
        assert result.type == "proj"

    def test_rejects_malformed_shape_with_invalid_id_error(self) -> None:
        with pytest.raises(InvalidIdError):
            decode_any("no-separator")

    def test_rejects_uppercase_hex(self) -> None:
        with pytest.raises(InvalidIdError):
            decode_any(f"usr_{SAMPLE_HEX.upper()}")

    def test_rejects_empty_type_prefix(self) -> None:
        with pytest.raises(InvalidIdError):
            decode_any(f"_{SAMPLE_HEX}")

    def test_rejects_nil_uuid(self) -> None:
        with pytest.raises(InvalidIdError):
            decode_any("usr_00000000000000000000000000000000")


class TestIsValidShape:
    """Predicate counterpart to decode_any."""

    def test_returns_true_for_application_defined_prefixes(self) -> None:
        assert is_valid_shape(f"proj_{SAMPLE_HEX}")
        assert is_valid_shape(f"doc_{SAMPLE_HEX}")

    def test_returns_true_for_registered_prefixes(self) -> None:
        assert is_valid_shape(f"usr_{SAMPLE_HEX}")

    def test_returns_false_for_malformed_shape(self) -> None:
        assert not is_valid_shape("not an id")
        assert not is_valid_shape(f"usr_{SAMPLE_HEX.upper()}")
        assert not is_valid_shape("usr_ffffffffffffffffffffffffffffffff")
