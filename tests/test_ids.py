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
    encode,
    generate,
    is_valid,
    type_of,
)


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
