#!/usr/bin/env python3
"""Regression-test schema string patterns against trailing line endings."""

from __future__ import annotations

import copy
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:
    sys.exit(
        "error: missing dependency 'jsonschema'\n"
        "  install it with: python3 -m pip install 'jsonschema[format]==4.26.0'"
    )

ROOT = Path(__file__).resolve().parent.parent

POLICY_DOCUMENT = {
    "origin": "https://service.example",
    "default_policy_selectors": {"GET": "policy-a"},
    "policy_selectors": {"POST": {"/resource": "policy-a"}},
    "policies": {
        "policy-a": {
            "purposes": {
                "site_rate_limit": {
                    "realm": "https://realm.example",
                    "profiles": {
                        "profile-a": {
                            "presentation_assurances": ["subject-present"]
                        }
                    },
                }
            }
        }
    },
}

REALM_DOCUMENT = {
    "realm": "https://realm.example",
    "profiles": {"profile-a": {}},
}

Document = dict[str, Any]
Mutation = Callable[[Document, str], None]


def rename(mapping: dict[str, Any], old: str, new: str) -> None:
    mapping[new] = mapping.pop(old)


def policy_profile_identifier(document: Document, value: str) -> None:
    profiles = document["policies"]["policy-a"]["purposes"]["site_rate_limit"][
        "profiles"
    ]
    rename(profiles, "profile-a", value)


def realm_profile_identifier(document: Document, value: str) -> None:
    rename(document["profiles"], "profile-a", value)


def presentation_assurance(document: Document, value: str) -> None:
    document["policies"]["policy-a"]["purposes"]["site_rate_limit"]["profiles"][
        "profile-a"
    ]["presentation_assurances"] = [value]


def default_selector_method(document: Document, value: str) -> None:
    rename(document["default_policy_selectors"], "GET", value)


def path_selector_method(document: Document, value: str) -> None:
    rename(document["policy_selectors"], "POST", value)


def default_selector_policy(document: Document, value: str) -> None:
    document["default_policy_selectors"]["GET"] = value


def path_selector_policy(document: Document, value: str) -> None:
    document["policy_selectors"]["POST"]["/resource"] = value


def path_selector_path_pattern(document: Document, value: str) -> None:
    rename(document["policy_selectors"]["POST"], "/resource", value)


def policy_definition_identifier(document: Document, value: str) -> None:
    rename(document["policies"], "policy-a", value)


def purpose_entry_name(document: Document, value: str) -> None:
    purposes = document["policies"]["policy-a"]["purposes"]
    rename(purposes, "site_rate_limit", value)


CASES: tuple[tuple[str, str, str, Mutation], ...] = (
    ("policy profile identifier", "policy", "profile-a", policy_profile_identifier),
    ("realm profile identifier", "realm", "profile-a", realm_profile_identifier),
    ("presentation assurance", "policy", "subject-present", presentation_assurance),
    ("default-selector method token", "policy", "GET", default_selector_method),
    ("path-selector method token", "policy", "POST", path_selector_method),
    (
        "default-selector policy identifier",
        "policy",
        "policy-a",
        default_selector_policy,
    ),
    ("path-selector policy identifier", "policy", "policy-a", path_selector_policy),
    ("path-selector path pattern", "policy", "/resource", path_selector_path_pattern),
    (
        "policy-definition identifier",
        "policy",
        "policy-a",
        policy_definition_identifier,
    ),
    ("purpose entry name", "policy", "site_rate_limit", purpose_entry_name),
)

LINE_ENDINGS = (("LF", "\n"), ("CR", "\r"), ("CRLF", "\r\n"))


def load_validator(filename: str) -> Draft202012Validator:
    path = ROOT / "schemas" / filename
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def main() -> int:
    validators = {
        "policy": load_validator("human-continuity-policy-metadata.schema.json"),
        "realm": load_validator("human-continuity-realm-metadata.schema.json"),
    }
    documents = {"policy": POLICY_DOCUMENT, "realm": REALM_DOCUMENT}
    failures = 0

    for label, schema_name, valid_value, mutate in CASES:
        valid_document = copy.deepcopy(documents[schema_name])
        mutate(valid_document, valid_value)
        errors = list(validators[schema_name].iter_errors(valid_document))
        if errors:
            print(f"FAIL  {label}: valid value rejected: {errors[0].message}")
            failures += 1

        for ending_name, ending in LINE_ENDINGS:
            invalid_document = copy.deepcopy(documents[schema_name])
            mutate(invalid_document, valid_value + ending)
            if validators[schema_name].is_valid(invalid_document):
                print(f"FAIL  {label}: trailing {ending_name} accepted")
                failures += 1

    checks = len(CASES) * (1 + len(LINE_ENDINGS))
    print(f"{checks} schema string-anchor checks, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
