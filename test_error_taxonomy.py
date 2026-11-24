#!/usr/bin/env python3
"""
Tests for error-taxonomy.py — one sample error per category.

Run directly:  python3 test_error_taxonomy.py
Or with pytest: pytest test_error_taxonomy.py
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "error_taxonomy", os.path.join(os.path.dirname(__file__), "error-taxonomy.py")
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
classify = _mod.classify

CASES = [
    # (sample error text, expected category, expected action)
    ("HTTP 401 Unauthorized: Invalid API Key provided", "AUTH", "rotate_key"),
    ("HTTPSConnectionPool: Connection refused by remote host", "PLATFORM_DEAD", "mark_dead"),
    ("429 Too Many Requests — rate limit exceeded", "RATE_LIMIT", "retry_backoff"),
    ("503 Service Unavailable: Internal server error", "TEMPORARY", "retry"),
    ("Error: model 'old-model-1' has been decommissioned by the provider", "MODEL_DEPRECATED", "update_model"),
    ("execution reverted: insufficient funds for gas * price + value", "INSUFFICIENT_FUNDS", "fund_wallet"),
    ("json.decoder.JSONDecodeError: Expecting value: line 1 column 1", "PARSING", "fix_parser"),
    ("the flux capacitor misaligned during phase two", "UNKNOWN", "investigate"),
]


def _check(text, expected_category, expected_action):
    category, info = classify(text)
    assert category == expected_category, f"{text!r}: got {category}, want {expected_category}"
    assert info["action"] == expected_action, f"{text!r}: got action {info['action']}, want {expected_action}"


def test_auth():
    _check(*CASES[0])


def test_platform_dead():
    _check(*CASES[1])


def test_rate_limit():
    _check(*CASES[2])


def test_temporary():
    _check(*CASES[3])


def test_model_deprecated():
    _check(*CASES[4])


def test_insufficient_funds():
    _check(*CASES[5])


def test_parsing():
    _check(*CASES[6])


def test_unknown():
    _check(*CASES[7])


if __name__ == "__main__":
    for text, cat, action in CASES:
        _check(text, cat, action)
        print(f"ok {cat} -> {action}")
    print(f"\n{len(CASES)} cases passed")
