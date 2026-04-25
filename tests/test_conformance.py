# Copyright 2026 NDC Digital, LLC
# SPDX-License-Identifier: Apache-2.0

"""Flametrench v0.1 conformance suite — Python harness.

Exercises the IDs capability against the fixture corpus vendored from
github.com/flametrench/spec/conformance/fixtures/ids/. The fixtures
under tests/conformance/fixtures/ are a snapshot; the drift-check CI
job verifies they match the upstream spec repo.

Every test name is "[{fixture_id}] {description}" so failures point
directly at a spec-linked fixture. Do not modify test behavior here;
if a fixture needs to change, change it in the spec repo and re-vendor.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from flametrench_ids import (
    InvalidIdError,
    InvalidTypeError,
    decode,
    encode,
    is_valid,
    type_of,
)

_FIXTURES_DIR = Path(__file__).parent / "conformance" / "fixtures"


def _load_fixture(relative_path: str) -> dict[str, Any]:
    raw = (_FIXTURES_DIR / relative_path).read_text(encoding="utf-8")
    return json.loads(raw)


def _error_class_for_spec_name(name: str) -> type[Exception]:
    if name == "InvalidIdError":
        return InvalidIdError
    if name == "InvalidTypeError":
        return InvalidTypeError
    raise RuntimeError(f"Unknown spec error name: {name}")


def _ids_param(relative_path: str) -> list[Any]:
    fixture = _load_fixture(relative_path)
    return [
        pytest.param(t, id=t["id"])
        for t in fixture["tests"]
    ]


# ─── ids.encode ───


@pytest.mark.parametrize("test_case", _ids_param("ids/encode.json"))
def test_encode_conformance(test_case: dict[str, Any]) -> None:
    inp = test_case["input"]
    expected = test_case["expected"]
    if "error" in expected:
        ctor = _error_class_for_spec_name(expected["error"])
        with pytest.raises(ctor):
            encode(inp["type"], inp["uuid"])
    else:
        assert encode(inp["type"], inp["uuid"]) == expected["result"]


# ─── ids.decode (positive + round-trip) ───


@pytest.mark.parametrize("test_case", _ids_param("ids/decode.json"))
def test_decode_positive_conformance(test_case: dict[str, Any]) -> None:
    inp = test_case["input"]
    expected = test_case["expected"]["result"]
    decoded = decode(inp["id"])
    assert decoded.type == expected["type"]
    assert decoded.uuid == expected["uuid"]


# ─── ids.decode (rejection) ───


@pytest.mark.parametrize("test_case", _ids_param("ids/decode-reject.json"))
def test_decode_rejection_conformance(test_case: dict[str, Any]) -> None:
    inp = test_case["input"]
    ctor = _error_class_for_spec_name(test_case["expected"]["error"])
    with pytest.raises(ctor):
        decode(inp["id"])


# ─── ids.is_valid ───


@pytest.mark.parametrize("test_case", _ids_param("ids/is-valid.json"))
def test_is_valid_conformance(test_case: dict[str, Any]) -> None:
    inp = test_case["input"]
    expected = test_case["expected"]["result"]
    if "expected_type" in inp:
        result = is_valid(inp["id"], inp["expected_type"])
    else:
        result = is_valid(inp["id"])
    assert result is expected


# ─── ids.type_of ───


@pytest.mark.parametrize("test_case", _ids_param("ids/type-of.json"))
def test_type_of_conformance(test_case: dict[str, Any]) -> None:
    inp = test_case["input"]
    expected = test_case["expected"]
    if "error" in expected:
        ctor = _error_class_for_spec_name(expected["error"])
        with pytest.raises(ctor):
            type_of(inp["id"])
    else:
        assert type_of(inp["id"]) == expected["result"]
