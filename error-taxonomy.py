#!/usr/bin/env python3
"""
Error Taxonomy — Classify failures and route to correct fix.
Usage: python3 error-taxonomy.py <error_message_or_file>
"""
import os, sys, json, re

TAXONOMY = {
    "AUTH": {
        "patterns": [r"401", r"Unauthorized", r"Invalid API Key", r"invalid_request_error.*invalid_api_key"],
        "action": "rotate_key",
        "description": "API key revoked, expired, or invalid"
    },
    "PLATFORM_DEAD": {
        "patterns": [r"404.*not found", r"DNS resolution failed", r"Connection refused", r"Platform database wiped"],
        "action": "mark_dead",
        "description": "Platform endpoint removed or service down"
    },
    "RATE_LIMIT": {
        "patterns": [r"429", r"Too Many Requests", r"rate limit exceeded", r"quota exceeded"],
        "action": "retry_backoff",
        "description": "Hit rate limit or quota"
    },
    "TEMPORARY": {
        "patterns": [r"500", r"502", r"503", r"504", r"Gateway timeout", r"Internal server error"],
        "action": "retry",
        "description": "Transient server error"
    },
    "MODEL_DEPRECATED": {
        "patterns": [r"decommissioned", r"deprecated", r"no longer supported", r"model.*removed"],
        "action": "update_model",
        "description": "Model string deprecated by provider"
    },
    "INSUFFICIENT_FUNDS": {
        "patterns": [r"insufficient funds", r"out of gas", r"execution reverted"],
        "action": "fund_wallet",
        "description": "Wallet lacks ETH/gas for transaction"
    },
    "PARSING": {
        "patterns": [r"JSONDecodeError", r"validation error", r"string_type.*input_value", r"missing.*field"],
        "action": "fix_parser",
        "description": "Response parsing failed (schema mismatch)"
    }
}

def classify(error_text):
    for category, info in TAXONOMY.items():
        for pattern in info["patterns"]:
            if re.search(pattern, error_text, re.IGNORECASE):
                return category, info
    return "UNKNOWN", {"action": "investigate", "description": "Unrecognized error pattern"}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 error-taxonomy.py '<error text>'")
        print("\nKnown categories:")
        for cat, info in TAXONOMY.items():
            print(f"  {cat}: {info['action']} — {info['description']}")
        return 0

    error_text = sys.argv[1]
    if error_text.startswith("/") and os.path.isfile(error_text):
        with open(error_text) as f:
            error_text = f.read()

    category, info = classify(error_text)
    result = {
        "category": category,
        "action": info["action"],
        "description": info["description"],
        "input_preview": error_text[:200]
    }
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
